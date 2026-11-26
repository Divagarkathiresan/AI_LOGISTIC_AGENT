
import re
import sqlglot

from sqlglot import exp


# Only these tables are allowed for querying.
ALLOWED_TABLES = {
    "customers",
    "orders",
    "delivery_partners",
    "shipments",
    "delivery_tracking"
}


def validate_sql(query: str) -> tuple[bool, str]:

    if not query or not query.strip():
        return False, "SQL query cannot be empty."

    query = query.strip()

    # Reject SQL comments.
    if "--" in query or "/*" in query or "*/" in query:
        return False, "SQL comments are not allowed."

    # Reject multiple statements.
    if ";" in query.rstrip(";"):
        return False, "Multiple SQL statements are not allowed."

    # Remove one optional trailing semicolon.
    query = query.rstrip(";").strip()

    try:
        # Parse SQL using MySQL dialect.
        parsed = sqlglot.parse(query, read="mysql")

        # Must contain exactly one statement.
        if len(parsed) != 1 or parsed[0] is None:
            return False, "Only one SQL statement is allowed."

        tree = parsed[0]

        # Only SELECT queries are allowed.
        if not isinstance(tree, exp.Query):
            return False, "Only SELECT queries are allowed."

        # A writable CTE can otherwise sit beneath an apparently read-only
        # top-level query. Reject any data-definition or data-modification
        # expression anywhere in the parsed statement.
        prohibited_names = (
            "Insert", "Update", "Delete", "Create", "Drop", "Alter",
            "Truncate", "Grant", "Revoke", "Command",
        )
        # sqlglot expression names vary slightly by release. Building this
        # tuple dynamically keeps the validator compatible with supported
        # releases without weakening the checks that are available.
        prohibited = tuple(
            expression for name in prohibited_names
            if (expression := getattr(exp, name, None)) is not None
        )
        if any(isinstance(node, prohibited) for node in tree.walk()):
            return False, "Only read-only SELECT queries are allowed."

        # Reject UNION and other set operations.
        if any(
            isinstance(node, (exp.Union, exp.Intersect, exp.Except))
            for node in tree.walk()
        ):
            return False, "Set operations are not allowed."

        # Reject SELECT INTO.
        if any(
            isinstance(node, exp.Into)
            for node in tree.walk()
        ):
            return False, "SELECT INTO is not allowed."

        # Reject locking reads.
        if any(
            isinstance(node, exp.Lock)
            for node in tree.walk()
        ):
            return False, "Locking queries are not allowed."

        # Check every physical table reference.
        for table in tree.find_all(exp.Table):

            table_name = table.name.lower()

            # CTE aliases are not physical database tables.
            if table_name in get_cte_names(tree):
                continue

            if table_name not in ALLOWED_TABLES:
                return False, f"Access to table '{table_name}' is not allowed."

        return True, "SQL query is valid."

    except sqlglot.errors.ParseError:
        return False, "Invalid SQL syntax."

    except Exception:
        return False, "SQL validation failed."


def get_cte_names(tree):

    names = set()

    for cte in tree.find_all(exp.CTE):
        names.add(cte.alias_or_name.lower())

    return names
