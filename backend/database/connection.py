
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from backend.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)

# Create database URL safely
database_url = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={"charset": "utf8mb4"}
)

# Create SQLAlchemy engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=3600
)


def test_connection():
    """
    Test the connection to MySQL.
    """

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text(
                    "SELECT DATABASE(), VERSION()"
                )
            )

            database_name, mysql_version = result.fetchone()

            print("MySQL connection successful!")
            print("Database:", database_name)
            print("MySQL Version:", mysql_version)

            return True

    except Exception as error:

        print("Database connection failed!")
        print("Error:", error)

        return False
