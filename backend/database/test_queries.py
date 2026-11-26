
from sqlalchemy import text

from backend.database.connection import engine


def get_customers():

    query = text("""
        SELECT
            customer_id,
            customer_name,
            email,
            city
        FROM customers
        ORDER BY customer_id
    """)

    with engine.connect() as connection:

        result = connection.execute(query)

        customers = result.mappings().all()

        for customer in customers:
            print(dict(customer))


if __name__ == "__main__":
    get_customers()
