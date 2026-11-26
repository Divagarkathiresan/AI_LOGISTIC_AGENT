
from backend.tools.sql_validator import validate_sql


test_queries = [
    (
        "Valid SELECT",
        "SELECT * FROM customers"
    ),
    (
        "Valid JOIN",
        """
        SELECT o.order_id, c.customer_name
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        """
    ),
    (
        "INSERT attack",
        "INSERT INTO customers(customer_name) VALUES ('Test')"
    ),
    (
        "UPDATE attack",
        "UPDATE orders SET status = 'Delivered'"
    ),
    (
        "DELETE attack",
        "DELETE FROM orders"
    ),
    (
        "DROP attack",
        "DROP TABLE customers"
    ),
    (
        "Unauthorized table",
        "SELECT * FROM customer_credentials"
    ),
    (
        "Multiple statements",
        "SELECT * FROM customers; DELETE FROM orders"
    ),
    (
        "Invalid syntax",
        "SELECT FROM customers"
    ),
    (
        "SELECT INTO attack",
        "SELECT * INTO backup FROM customers"
    )
]


for name, query in test_queries:

    is_valid, message = validate_sql(query)

    print("-" * 60)
    print("Test:", name)
    print("Allowed:", is_valid)
    print("Message:", message)
