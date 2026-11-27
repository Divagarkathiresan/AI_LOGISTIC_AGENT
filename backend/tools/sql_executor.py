
import logging
import json

from sqlalchemy import text
from langchain_core.tools import tool
from backend.database.connection import engine
from backend.tools.sql_validator import validate_sql


logger = logging.getLogger(__name__)

def execute_sql(query: str) -> dict:

    # This is the SQL emitted by the LLM in its tool call.  ``flush=True`` is
    # important when Streamlit is running the app because stdout can otherwise
    # remain buffered instead of appearing in the process terminal.
    print(f"\nGenerated SQL query:\n{query}\n", flush=True)

    # Step 1: Validate generated SQL.
    is_valid, message = validate_sql(query)
    print(f"[Backend] SQL validation result: {is_valid}", flush=True)

    if not is_valid:
        return {
            "success": False,
            "error": message
        }

    try:
        # Step 2: Execute only validated SQL.
        with engine.connect() as connection:

            result = connection.execute(text(query))

            # Step 3: Return every row requested by the validated query.
            rows = result.mappings().all()

            records = [dict(row) for row in rows]
            print(
                f"[Backend] SQL execution returned {len(records)} row(s).",
                flush=True,
            )

            # Step 4: Convert database results to JSON.
            return {
                "success": True,
                "row_count": len(records),
                "data": records
            }

    except Exception:
        # Full details stay in server logs.
        logger.exception("SQL execution failed")

        # User receives only a safe message.
        return {
            "success": False,
            "error": "The database could not execute the query."
        }


@tool(response_format="content_and_artifact")
def execute_sql_query(query: str) -> tuple[str, dict]:
    """Execute one validated, read-only MySQL SELECT query.

    The query is checked for unsafe operations and restricted to the logistics
    tables before execution. Returns a compact summary to the LLM and keeps
    complete rows as an internal artifact for the UI.
    """
    result = execute_sql(query)
    if result.get("success"):
        content = json.dumps({
            "success": True,
            "row_count": result["row_count"],
            "message": (
                "Query completed. Give a concise summary; the UI will display "
                "the complete result rows."
            ),
        })
    else:
        content = json.dumps(result, default=str)

    # LangChain includes only `content` in the next model request. `result`
    # remains attached to the ToolMessage as an artifact for Streamlit, which
    # prevents large result sets from exceeding the Groq token limit.
    return content, result
