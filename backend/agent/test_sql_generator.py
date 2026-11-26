
from backend.agent.sql_generator import generate_sql


def main():

    questions = [
        "Show all customers",

        "Find all delayed shipments",

        "Show shipments handled by Suresh",

        "Find the total number of shipments",

        "Find the total order amount for each customer",

        "Show the latest tracking status of every shipment",

        "Find the delivery partner who handles the most shipments"
    ]

    for question in questions:

        print("\n" + "=" * 70)

        print("USER QUESTION:")
        print(question)

        print("\nGENERATED SQL:")

        try:

            sql_query = generate_sql(question)

            print(sql_query)

        except Exception as error:

            print("Error:", error)


if __name__ == "__main__":
    main()
