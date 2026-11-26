
from sqlalchemy import inspect

from backend.database.connection import engine


def get_database_schema():
    """
    Dynamically discovers tables, columns,
    primary keys and foreign keys.
    """

    inspector = inspect(engine)

    schema = {}

    # Discover all table names
    table_names = inspector.get_table_names()

    for table_name in table_names:

        # Discover columns
        columns = inspector.get_columns(table_name)

        # Discover primary key
        primary_key = inspector.get_pk_constraint(
            table_name
        )

        primary_key_columns = primary_key.get(
            "constrained_columns", []
        )

        # Discover foreign keys
        foreign_keys = inspector.get_foreign_keys(
            table_name
        )

        # Store table information
        schema[table_name] = {
            "columns": [],
            "primary_key": primary_key_columns,
            "foreign_keys": []
        }

        # Process columns
        for column in columns:

            column_info = {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"]
            }

            schema[table_name]["columns"].append(
                column_info
            )

        # Process foreign keys
        for fk in foreign_keys:

            fk_info = {
                "columns": fk["constrained_columns"],
                "referenced_table": fk["referred_table"],
                "referenced_columns": fk["referred_columns"]
            }

            schema[table_name]["foreign_keys"].append(
                fk_info
            )

    return schema


def format_schema_for_llm():
    """
    Converts discovered schema into readable text.
    This will later be provided to the LLM.
    """

    schema = get_database_schema()

    schema_description = []

    for table_name, details in schema.items():

        schema_description.append(
            f"\nTable: {table_name}"
        )

        schema_description.append("Columns:")

        for column in details["columns"]:

            schema_description.append(
                f"- {column['name']} "
                f"({column['type']})"
            )

        schema_description.append(
            f"Primary Key: {details['primary_key']}"
        )

        schema_description.append("Foreign Keys:")

        for fk in details["foreign_keys"]:

            schema_description.append(
                f"- {fk['columns']} references "
                f"{fk['referenced_table']}"
                f"({fk['referenced_columns']})"
            )

    return "\n".join(schema_description)
