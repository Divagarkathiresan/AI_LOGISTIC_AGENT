# AI-Powered Logistics SQL Agent — Project Explanation

## 1. Project objective

This project is an internal logistics assistant.
It answers natural-language questions about customers, orders, shipments,
delivery partners, and delivery tracking by querying the existing MySQL
logistics database.

Example questions:

- “Give Arun Kumar orders.”
- “Show delayed shipments with customer names.”
- “Which delivery partner handles the most shipments?”
- “Where is shipment SH1002?”
- “I am Divagar” followed by “Show my orders.”

The application does **not** use fixed SQL templates or hardcoded answers.
The LLM generates a query dynamically after inspecting the active database
schema.

## 2. Main architecture

```text
Streamlit UI
    |
    v
SQL Agent (LangChain + Groq LLM)
    |----> Conversation memory
    |----> Schema discovery tool
    |           |
    |           v
    |        Existing MySQL database
    |
    |----> SQL execution tool
                |
                v
          SQL safety validator
                |
                v
          Read-only MySQL SELECT query
```

The project uses the database connection configured in `.env`. 

## 3. Database layer

### Existing logistics database

The agent works with these connected tables:

| Table | Purpose |
| --- | --- |
| `customers` | Customer details |
| `orders` | Orders placed by customers |
| `shipments` | Shipment details for orders |
| `delivery_partners` | Delivery-partner information |
| `delivery_tracking` | Tracking events for shipments |

The relationships are discovered dynamically with SQLAlchemy inspection:

- `orders.customer_id` → `customers.customer_id`
- `shipments.order_id` → `orders.order_id`
- `shipments.partner_id` → `delivery_partners.partner_id`
- `delivery_tracking.shipment_id` → `shipments.shipment_id`

### Relevant code

- `backend/config.py`: loads MySQL and Groq settings from `.env`.
- `backend/database/connection.py`: creates the SQLAlchemy MySQL engine.
- `backend/database/schema.py`: discovers tables, columns, primary keys, and
  foreign keys at runtime and formats them for the LLM.

This schema discovery is important because the model receives the real schema
instead of relying on guessed table or column names.

## 4. AI SQL Agent workflow

The central workflow is implemented in `backend/agent/sql_agent.py`.

1. The user submits a natural-language question in Streamlit.
2. The app sends the question and a per-session ID to `run_sql_agent`.
3. The agent restores earlier user and assistant messages from memory as real
   chat turns.
4. The Groq model receives the operations-agent system prompt, conversation
   history, and current question.
5. The model calls `get_database_schema` to inspect the active database.
6. The model creates a dynamic SQL `SELECT` query based on the question and
   schema.
7. The model calls `execute_sql_query`.
8. The query is validated before it reaches MySQL.
9. The validated query executes and returns structured rows.
10. The model converts the returned rows into a clear natural-language answer.
11. The user question and final answer are saved to memory for future
    follow-up questions.

The model can generate joins, filtering, sorting, aggregations, subqueries,
CTEs, and window functions when they are appropriate for the request.

## 5. Tools used by the agent

### `get_database_schema`

Defined in `backend/tools/schema_tool.py`.

This tool calls `format_schema_for_llm()` and returns:

- table names;
- columns and types;
- primary keys; and
- foreign-key relationships.

It allows the LLM to understand how to join real tables correctly.

### `execute_sql_query`

Defined in `backend/tools/sql_executor.py`.

This LangChain tool:

1. accepts one SQL query from the model;
2. validates it with `validate_sql`;
3. executes it only if it is safe;
4. limits output to 100 rows; and
5. returns structured JSON-compatible data to the model.

The rows are used to formulate the answer but are intentionally not displayed
as raw tables in the final chat interface.

## 6. SQL safety and validation

`backend/tools/sql_validator.py` protects the database from unsafe generated
SQL.

The validator uses `sqlglot` with the MySQL dialect and enforces:

- only one statement is allowed;
- only read-only `SELECT`/query expressions are allowed;
- SQL comments are rejected;
- DDL and modification operations such as `INSERT`, `UPDATE`, `DELETE`,
  `DROP`, `ALTER`, and `CREATE` are rejected;
- locking reads and `SELECT INTO` are rejected;
- only approved logistics tables can be queried;
- set operations such as `UNION`, `INTERSECT`, and `EXCEPT` are rejected.

The separate `customer_credentials` table in the configured database is not in
the allowed table list and therefore cannot be accessed by the agent.

## 7. Input and output guardrails

`backend/tools/guardrails.py` protects the application before the LLM is
called and before an answer is displayed.

### Input guardrails

Every user message is checked before it can reach the LLM, schema tool, or
database. The guardrail:

- rejects empty input;
- limits a question to 500 characters;
- normalizes repeated whitespace; and
- rejects common prompt-injection attempts such as “ignore previous
  instructions”, attempts to reveal the system prompt, and jailbreak requests.

The application also has a logistics scope guard in `sql_agent.py`. Requests
must be about customers, orders, shipments, delivery partners, or tracking.
Clear follow-up questions to an earlier logistics request are allowed; general
knowledge, coding, entertainment, and personal-advice requests are not sent to
the LLM or database.

### Output guardrails

Every final model response passes through `sanitize_output` before it reaches
the Streamlit page. It:

- replaces an empty model response with a safe message;
- blocks responses that appear to contain API keys, database passwords, or
  other configuration secrets;
- blocks a response that begins with raw SQL (`SELECT`, `WITH`, `INSERT`, and
  similar statements); and
- strips Markdown SQL code-fence markers.

This is an additional protection layer. The system prompt already tells the
model to provide a plain-language logistics answer, while the SQL validator
ensures that generated database queries are read-only.

## 8. Conversation memory

Memory is implemented in `backend/memory/conversation_memory.py`.

- Each Streamlit browser session receives a unique `session_id`.
- The memory stores the latest 10 user/assistant messages for that session.
- A name explicitly given as “I am …” or “My name is …” is stored as a
  session-only customer profile value.
- `backend/agent/context_manager.py` saves the completed user question and
  final assistant answer.
- Before processing a new question, `sql_agent.py` restores this history as
  `HumanMessage` and `AIMessage` objects.

This allows conversational follow-ups. For example:

```text
User: I am Divagar.
Assistant: Thanks, Divagar. I've saved your name for this session.
User: Show my orders.
Assistant: [Looks up Divagar's orders in the database]
```

Using role-specific messages is important: it preserves the meaning of each
previous turn better than sending the entire conversation as one text block.
The saved name is also passed to the agent as an explicit session context value
so the model can reliably resolve “my orders.” The profile is cleared when the
user selects **New Conversation**.

## 9. Frontend design

The web application is in `frontend/app.py` and uses Streamlit.

Features implemented:

- chat input for natural-language logistics questions;
- a unique session ID for each conversation;
- **New Conversation** button that clears only that session's memory;
- user messages displayed on the right;
- Logistics Assistant replies displayed on the left;
- no generated SQL is exposed in the UI;
- no raw result tables are exposed below answers.

Keeping SQL and raw rows internal makes the interface suitable for normal
operations users. The agent instead gives the retrieved information as a clear
natural-language response.

## 10. Important implementation decisions

### Internal company use

The system prompt identifies the user as authorized company operations staff.
Therefore, a named request such as “Give Arun Kumar orders” is treated as a
valid database lookup and does not unnecessarily ask for email, customer ID,
or authorization confirmation.

### Dynamic SQL, not hardcoded answers

The database schema and user question are supplied to the LLM at runtime.
The generated SQL is then validated and executed. The agent does not contain a
list of prewritten answers for example questions.

### Raw database information is protected

The LLM can use data returned by the execution tool, but it is instructed to
respond with a readable answer rather than SQL code or unprocessed tool output.

### Failure handling

- Blank questions are rejected before calling the LLM.
- Missing Groq configuration gives a clear configuration error when the model
  is used.
- Database errors are logged on the server and returned as a safe generic
  error message rather than exposing implementation details.
- Invalid SQL never reaches the database.

## 11. Demonstration steps for the trainer

1. Start the app:

   ```bash
   streamlit run frontend/app.py
   ```

2. Ask a direct lookup question:

   ```text
   Give Arun Kumar orders
   ```

3. Ask a multi-table question:

   ```text
   Show delayed shipments with customer names and delivery partners
   ```

4. Ask an aggregation question:

   ```text
   Which delivery partner handles the most shipments?
   ```

5. Demonstrate memory:

   ```text
   I am Divagar
   Show my orders
   ```

6. Explain that each generated query goes through the read-only SQL validator
   before execution and that raw SQL is intentionally hidden from the user.

## 12. Project file guide

| File/folder | Responsibility |
| --- | --- |
| `frontend/app.py` | Streamlit interface and session handling |
| `backend/agent/sql_agent.py` | Tool-calling agent loop and memory replay |
| `backend/agent/agent_prompt.py` | Agent responsibilities and behavior rules |
| `backend/agent/llm.py` | Groq LLM setup |
| `backend/database/connection.py` | MySQL SQLAlchemy connection |
| `backend/database/schema.py` | Dynamic schema/relationship discovery |
| `backend/tools/schema_tool.py` | Schema tool exposed to the LLM |
| `backend/tools/sql_executor.py` | Validated SQL execution tool |
| `backend/tools/sql_validator.py` | Read-only SQL security rules |
| `backend/tools/guardrails.py` | Input validation and output sanitization |
| `backend/memory/conversation_memory.py` | Per-session in-memory chat history |
| `database_setup.sql` | Optional fresh demo database schema/data |
| `README.md` | Setup and usage instructions |
