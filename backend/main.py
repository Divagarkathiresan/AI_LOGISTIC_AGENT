
from backend.database.connection import test_connection
from backend.database.schema import (
    get_database_schema,
    format_schema_for_llm
)


def main():

    print("=" * 60)
    print("LOGISTICS SQL AGENT - DATABASE TEST")
    print("=" * 60)

    # Step 1: Test connection
    connected = test_connection()

    if not connected:
        print("Please check your database configuration.")
        return

    # Step 2: Discover schema
    print("\nDATABASE SCHEMA DISCOVERY")

    schema = get_database_schema()

    for table_name, details in schema.items():

        print(f"\nTable: {table_name}")

        print("Columns:")

        for column in details["columns"]:
            print(
                f"  {column['name']} : {column['type']}"
            )

        print("Primary Key:", details["primary_key"])

        print("Foreign Keys:", details["foreign_keys"])

    # Step 3: Format schema
    print("\n" + "=" * 60)
    print("SCHEMA DESCRIPTION FOR LLM")
    print("=" * 60)

    print(format_schema_for_llm())


if __name__ == "__main__":
    main()
