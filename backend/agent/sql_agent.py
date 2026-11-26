
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from langchain.agents import create_agent
import json
import logging
import ast
from collections import defaultdict

from backend.agent.llm import get_llm
from backend.agent.agent_prompt import AGENT_SYSTEM_PROMPT
from backend.agent.context_manager import save_conversation
from backend.memory.conversation_memory import conversation_memory

from backend.tools.schema_tool import get_database_schema
from backend.tools.sql_executor import execute_sql_query
from backend.tools.guardrails import classify_input, sanitize_output, validate_input


logger = logging.getLogger(__name__)


# Register available tools
TOOLS = [
    get_database_schema,
    execute_sql_query
]

def create_logistics_agent(llm):
    """Create the LangChain tool-calling agent for valid logistics requests."""
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=AGENT_SYSTEM_PROMPT,
        name="logistics_sql_agent",
    )


def run_sql_agent(question: str, session_id: str = "default"):
    """
    Execute a complete tool-calling SQL Agent workflow.
    """

    input_is_valid, input_result = validate_input(question)
    if not input_is_valid:
        return {
            "success": False,
            "question": question,
            "answer": input_result,
            "sql_queries": [],
            "tool_history": [],
            "sql": None,
            "data": None,
            "query_succeeded": False,
        }
    question = input_result

    # Build the conversation supplied to the agent.
    history = conversation_memory.get_history(session_id)
    messages = []

    # Replay the session as proper chat turns. Supplying the history as one
    # text blob makes it easy for a model to overlook facts such as “I am
    # Divagar”; role-specific messages preserve the conversational meaning.
    for message in history:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content=message["content"]))

    messages.append(HumanMessage(content=question))

    # LLM setup and execution can both fail because of configuration or
    # provider errors, so handle them through the same safe response path.
    try:
        llm = get_llm()
        input_allowed, _ = classify_input(llm, question, history)
        if not input_allowed:
            answer = (
                "I can help only with logistics questions about customers, orders, "
                "shipments, delivery partners, and delivery tracking."
            )
            result = {
                "success": True,
                "question": question,
                "answer": answer,
                "sql_queries": [],
                "tool_history": [],
            }
            _add_display_fields(result)
            save_conversation(session_id, question, answer)
            
            return result
        
        agent = create_logistics_agent(llm)
        agent_state = agent.invoke(
            {"messages": messages}
        )

    except Exception as error:
        # Keep the full provider/database failure in the terminal while
        # returning a safe, non-technical response to the chat user.
        logger.exception("Logistics agent failed while processing: %s", question)
        error_text = str(error).lower()
        if (
            getattr(error, "status_code", None) == 429
            or "rate limit" in error_text
            or "rate_limit" in error_text
        ):
            answer = (
                "The AI service has reached its request or token limit. "
                "Please wait a few minutes and try your order request again."
            )
        else:
            answer = "I could not complete that logistics request."
        result = {
            "success": False,
            "question": question,
            "answer": answer,
            "sql_queries": [],
            "tool_history": [],
        }
        _add_display_fields(result)
        save_conversation(session_id, question, result["answer"])
        return result

    agent_messages = agent_state.get("messages", [])
    executed_queries, tool_history = _extract_tool_activity(agent_messages)
    print(
        "[Backend] Extracted "
        f"{len(executed_queries)} SQL query/queries and "
        f"{len(tool_history)} tool call(s).",
        flush=True,
    )
    final_message = next(
        (message for message in reversed(agent_messages)
         if isinstance(message, AIMessage) and not message.tool_calls),
        None,
    )

    result = {
        "success": final_message is not None,
        "question": question,
        "answer": sanitize_output(
            final_message.content if final_message else
            "I could not complete that logistics request."
        ),
        "sql_queries": executed_queries,
        "tool_history": tool_history,
    }
    _add_display_fields(result)
    save_conversation(session_id, question, result["answer"])
    return result


def _extract_tool_activity(messages):
    """Collect internal tool activity from the LangChain agent message trace."""
    tool_results = {}
    tool_results_by_name = defaultdict(list)
    for message in messages:
        if isinstance(message, ToolMessage):
            tool_result = _parse_tool_result(message.content)
            tool_results[message.tool_call_id] = tool_result
            if message.name:
                tool_results_by_name[message.name].append(tool_result)

    executed_queries = []
    tool_history = []
    for message in messages:
        if not isinstance(message, AIMessage):
            continue
        for tool_call in message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            if tool_name == "execute_sql_query":
                executed_queries.append(tool_args.get("query", ""))
            tool_result = tool_results.get(tool_call["id"])
            if tool_result is None and tool_results_by_name[tool_name]:
                # Fall back to tool name and call order for providers that
                # rewrite tool-call IDs in their message trace.
                tool_result = tool_results_by_name[tool_name].pop(0)
            tool_history.append({
                "tool": tool_name,
                "arguments": tool_args,
                "result": tool_result if tool_result is not None
                else "No tool result returned.",
            })
    return executed_queries, tool_history


def _parse_tool_result(content):
    """Normalize JSON, Python-literal, and content-block tool responses."""
    if isinstance(content, dict):
        return content
    if isinstance(content, list):
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    if not isinstance(content, str):
        return content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(content)
        except (ValueError, SyntaxError):
            return content


def _add_display_fields(result: dict) -> None:
    """Expose the last successful query result in the UI-friendly shape."""
    result["sql"] = result["sql_queries"][-1] if result["sql_queries"] else None
    result["data"] = None
    result["query_succeeded"] = False
    for item in reversed(result["tool_history"]):
        if item["tool"] != "execute_sql_query":
            continue
        tool_result = item["result"]
        # Tool calls return a dict; tolerate a string in case a provider
        # serializes it before it reaches this workflow.
        if isinstance(tool_result, dict) and tool_result.get("success"):
            result["query_succeeded"] = True
            result["data"] = tool_result.get("data", [])
        break
