
import logging

from sqlalchemy import text
from langchain_core.tools import tool
from backend.database.connection import engine
from backend.tools.sql_validator import validate_sql


logger = logging.getLogger(__name__)

MAX_ROWS = 100


def execute_sql(query: str) -> dict:

    # Step 1: Validate generated SQL.
    is_valid, message = validate_sql(query)

    if not is_valid:
        return {
            "success": False,
            "error": message
        }

    try:
        # Step 2: Execute only validated SQL.
        with engine.connect() as connection:

            result = connection.execute(text(query))

            # Step 3: Fetch a limited number of rows.
            rows = result.mappings().fetchmany(MAX_ROWS)

            records = [dict(row) for row in rows]

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


@tool
def execute_sql_query(query: str) -> dict:
    """Execute one validated, read-only MySQL SELECT query.

    The query is checked for unsafe operations and restricted to the logistics
    tables before execution. Returns structured rows or a safe error message.
    """
    return execute_sql(query)
