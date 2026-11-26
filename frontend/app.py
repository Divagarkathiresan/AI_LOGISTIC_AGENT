
import uuid
import sys
from pathlib import Path

import streamlit as st

# Streamlit runs this file with ``frontend`` as the script location. Add the
# project root so the sibling ``backend`` package is importable regardless of
# the directory from which ``streamlit run`` is launched.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.agent.sql_agent import run_sql_agent
from backend.memory.conversation_memory import conversation_memory


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Logistics SQL Agent",
    page_icon="📦",
    layout="wide"
)

st.title("📦 AI-Powered Logistics SQL Agent")

st.caption(
    "Ask questions about customers, orders, shipments "
    "and delivery tracking using natural language."
)


def render_message(role: str, content: str) -> None:
    """Render company-chat messages with the user on the right."""
    left_column, right_column = st.columns([1, 1])

    if role == "user":
        with right_column:
            st.markdown("**You**")
            st.markdown(content)
    else:
        with left_column:
            st.markdown("**Logistics Assistant**")
            st.markdown(content)


def render_query_result(message: dict) -> None:
    """Render persisted SQL and rows for an assistant chat message."""
    if message.get("sql"):
        with st.expander("Generated SQL", expanded=False):
            st.code(message["sql"], language="sql")

    if message.get("query_succeeded"):
        with st.expander("", expanded=True):
            data = message.get("data", [])
            if data:
                st.caption(f"{len(data)} row(s) returned")
                st.dataframe(data, use_container_width=True)
            else:
                st.info("The query completed but returned no records.")


# --------------------------------------------------
# SESSION MANAGEMENT
# --------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_sql" not in st.session_state:
    st.session_state.last_sql = None

if "last_results" not in st.session_state:
    st.session_state.last_results = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("Conversation")

    st.write("Session ID:")
    st.code(st.session_state.session_id[:12])

    if st.button("➕ New Conversation", use_container_width=True):

        conversation_memory.clear_history(
            st.session_state.session_id
        )

        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.last_sql = None
        st.session_state.last_results = None

        st.rerun()

    st.divider()

    st.subheader("About")

    st.write(
        ""
    )


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:
    render_message(message["role"], message["content"])
    if message["role"] == "assistant":
        render_query_result(message)


# --------------------------------------------------
# PROCESS USER INPUT
# --------------------------------------------------

user_question = st.chat_input(
    "Ask something about orders, shipments or deliveries..."
)


if user_question:

    # Display user question.
    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    render_message("user", user_question)

    # Call backend agent.
    with st.spinner("Analyzing your question..."):

        try:

            response = run_sql_agent(
                question=user_question,
                session_id=st.session_state.session_id
            )

            answer = response.get(
                "answer",
                "I couldn't generate an answer."
            )

            render_message("assistant", answer)

            assistant_message = {
                "role": "assistant",
                "content": answer,
                "data": response.get("data", []),
                "query_succeeded": response.get("query_succeeded", False),
            }
            render_query_result(assistant_message)
            st.session_state.messages.append(assistant_message)

        except Exception:
            st.error(
                "Something went wrong while processing "
                "your question. Please try again."
            )

    st.rerun()
