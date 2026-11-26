# AI-Powered Logistics SQL Agent

A Streamlit chat app that converts natural-language logistics questions into dynamic, read-only MySQL queries using a Groq tool-calling model. It discovers the live schema, executes validated SQL, displays the SQL and tabular rows, and keeps short per-session context for follow-up questions.

## Features

- Five related tables: `customers`, `orders`, `shipments`, `delivery_partners`, and `delivery_tracking`
- Runtime schema discovery, including primary and foreign keys
- Dynamic natural-language-to-SQL—no fixed query templates
- Joins, filters, sorting, aggregation, subqueries, CTEs, and window functions
- Read-only SQL validation: one statement, no comments, no DDL/DML/locking reads, and only approved logistics tables
- Streamlit chat UI with generated SQL and structured results

## Setup

1. Point the app at your existing MySQL 8.0+ logistics database. Create `.env`
   in the repository root:

   ```dotenv
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_NAME=logistics_db
   GROQ_API_KEY=your_groq_key
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

2. Install and run:

   ```bash
   python -m pip install -r requirements.txt
   streamlit run frontend/app.py
   ```

## Example questions

- “Show delayed shipments with customer names.”
- “Which delivery partner handles the most shipments?”
- “Where is shipment SH1002?”
- “Show the latest tracking status of every shipment.”

Run `python backend/tools/test_sql_security.py` to exercise the SQL safety
checks. The script demonstrates rejection of modification and multi-statement
SQL. Database/LLM checks require the configured MySQL instance and Groq key.

`database_setup.sql` is included only as an optional fresh-demo database
template. The application never runs it automatically; when `.env` is set, all
schema discovery and query results come from that configured database.
