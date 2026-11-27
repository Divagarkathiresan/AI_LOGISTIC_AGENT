This project is an AI-powered Logistics SQL Assistant built for company operations users to ask natural-language questions about customers, orders, shipments, delivery partners, and delivery tracking. The Streamlit web application receives a question, assigns the browser session a unique ID, and sends the question to the backend SQL agent. First, deterministic validation checks that the input is present and within the allowed length, then a structured LLM-based guardrail classifies whether the request is a safe logistics read request; this also uses the last three chat exchanges so that clear follow-ups, such as supplying a customer name after the agent asks for one, can be understood. The LangChain agent receives the current question, recent conversation context, and a concise system prompt, then calls the schema-discovery tool to inspect the real MySQL database tables, columns, primary keys, and foreign-key relationships. Using that live schema, rather than predefined queries or hardcoded answers, the LLM dynamically creates the required MySQL query and can use joins, filters, sorting, grouping, aggregations, subqueries, and CTEs when needed. Before any SQL reaches MySQL, the SQL validator uses sqlglot to allow only one read-only SELECT-style statement, reject comments, multiple statements, locking reads, SELECT INTO, UNION-style operations, DDL and DML commands such as INSERT, UPDATE, DELETE, DROP, ALTER, and CREATE, and restrict access to the five approved logistics tables: customers, orders, shipments, delivery_partners, and delivery_tracking. The validated query is executed with SQLAlchemy, its rows are returned as JSON, and the agent gives a concise answer based only on confirmed results; the Streamlit interface can retain the structured result for display while generated SQL remains available in the server terminal for debugging. The backend also prints workflow progress, generated SQL, validation status, and returned row counts in the terminal, while error handling returns safe user messages and records full technical tracebacks only on the server. Overall, the workflow is Streamlit chat interface to input guardrail to LangChain/Groq SQL agent to schema discovery and SQL generation to SQL validation to read-only MySQL execution to structured result and natural-language response, providing a dynamic, conversational, and secure logistics data assistant.

classify_input
Checks whether a user’s message is a safe and relevant logistics request before the SQL agent runs. It uses the recent three-chat context, so it can understand follow-ups such as a customer name given after the agent asks for one. It blocks unrelated, unsafe, or instruction-override requests.

_extract_tool_activity
Reads the LangChain agent’s internal message history after execution. It collects which tools were called, the SQL generated for execute_sql_query, and the corresponding tool results.

_parse_tool_result
Converts tool output into usable Python data. LangChain can return results as JSON text, Python dictionary text, or structured content blocks; this function supports all those formats.

_add_display_fields
Converts the internal tool history into frontend-friendly values: the latest SQL query, returned database rows, and a query_succeeded flag. Streamlit uses these values to decide whether it can display query results.


1. User Input
   ↓
   User enters a natural-language logistics question in the Streamlit UI.
   Example: “Show all delayed shipments.”

2. Frontend Session Handling
   ↓
   frontend/app.py creates or uses a unique session ID and sends the question
   to run_sql_agent() in backend/agent/sql_agent.py.

3. Basic Input Validation
   ↓
   validate_input() in backend/tools/guardrails.py checks:
   - Input is not empty
   - Input length is within the allowed limit
   - Whitespace is normalized

4. LLM Input Guardrail
   ↓
   classify_input() uses the LLM and the previous three chat exchanges to decide:
   - Is this a logistics request?
   - Is it a valid follow-up?
   - Is it a prompt-injection or unrelated request?
   - Is it requesting unsafe database modifications?
   Invalid requests are stopped here.

5. Conversation Memory
   ↓
   The agent loads only the last three user/assistant chat exchanges from
   backend/memory/conversation_memory.py.
   This helps it understand follow-up questions.

6. Agent Creation
   ↓
   create_logistics_agent() creates a LangChain agent using:
   - Groq LLM
   - System prompt from agent_prompt.py
   - get_database_schema tool
   - execute_sql_query tool

7. Schema Discovery
   ↓
   The agent calls get_database_schema() from schema_tool.py.
   It reads the live MySQL schema using SQLAlchemy and returns:
   - Table names
   - Columns and data types
   - Primary keys
   - Foreign-key relationships

8. Dynamic SQL Generation
   ↓
   Based on the user question and discovered schema, the LLM dynamically
   generates a SQL query. No fixed SQL templates are used.
   It can generate SELECT queries with joins, filters, sorting, GROUP BY,
   aggregations, subqueries, and CTEs.

9. SQL Query Execution Tool
   ↓
   The agent calls execute_sql_query(query="SELECT ...").

10. SQL Validation
    ↓
    validate_sql() in sql_validator.py checks:
    - Only one SQL statement
    - Read-only SELECT query only
    - No INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or TRUNCATE
    - No comments, locking reads, SELECT INTO, or set operations
    - Only approved logistics tables are accessed

11. Database Execution
    ↓
    If validation succeeds, sql_executor.py executes the query through
    SQLAlchemy against MySQL and fetches the returned rows.

12. Tool Result Parsing
    ↓
    The SQL result is returned as JSON.
    _parse_tool_result() converts tool output into Python data.
    _extract_tool_activity() collects generated SQL and tool results.
    _add_display_fields() prepares data, SQL status, and rows for the UI.

13. Natural-Language Response
    ↓
    The LLM reads the confirmed database result and produces a concise
    logistics answer. sanitize_output() removes unsafe output if necessary.

14. UI Display and Memory Save
    ↓
    Streamlit displays the assistant response and, when enabled, structured
    query results. The user question and assistant response are saved, while
    only the latest three chat exchanges are retained.

15. Terminal Logging
    ↓
    The backend terminal prints:
    - Input-validation status
    - Agent progress
    - Generated SQL
    - SQL validation result
    - Returned row count
    - Any backend traceback/error