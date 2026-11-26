
from langchain.tools import tool

from backend.database.schema import format_schema_for_llm


@tool
def get_database_schema() -> str:
    """
    Discover the logistics database schema.

    Returns all available table names, columns,
    data types, primary keys and foreign keys.

    Use this tool to understand database structure
    before generating SQL queries.
    """

    schema = format_schema_for_llm()

    return schema
