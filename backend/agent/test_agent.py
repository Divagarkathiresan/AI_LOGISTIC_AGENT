
from backend.agent.sql_agent import run_sql_agent


def main():

    questions = [
        "Show all delayed shipments with customer names.",

        "Show all shipments handled by Suresh.",

        "Find the total number of shipments.",

        "Show the latest tracking status of every shipment.",

        "Where is shipment SH1001?",

        "Where is my order?"
    ]

    for question in questions:

        print("\n" + "=" * 70)

        print("USER QUESTION:")
        print(question)

        try:

            result = run_sql_agent(question)

            print("\nGENERATED SQL:")

            for query in result["sql_queries"]:
                print(query)

            print("\nTOOL EXECUTION HISTORY:")

            for item in result["tool_history"]:
                print("Tool:", item["tool"])

            print("\nAGENT RESPONSE:")
            print(result["answer"])

        except Exception as error:

            print("Agent Error:", error)


if __name__ == "__main__":
    main()
