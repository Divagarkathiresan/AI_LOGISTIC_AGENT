
from langchain_core.output_parsers import StrOutputParser

from backend.agent.llm import get_llm
from backend.agent.prompts import SQL_GENERATION_PROMPT
from backend.database.schema import format_schema_for_llm


def generate_sql(question: str):

    """
    Generate SQL dynamically from a natural-language
    question using the discovered database schema.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # Step 1: Discover database schema
    schema = format_schema_for_llm()

    # Step 2: Initialize LLM
    llm = get_llm()

    # Step 3: Create the LangChain pipeline
    sql_chain = (
        SQL_GENERATION_PROMPT
        | llm
        | StrOutputParser()
    )

    # Step 4: Send schema and user question
    response = sql_chain.invoke({
        "schema": schema,
        "question": question
    })

    # Step 5: Clean the response
    sql_query = response.strip()

    if sql_query.startswith("```"):
        sql_query = sql_query.replace(
            "```sql", ""
        ).replace("```", "").strip()

    return sql_query
