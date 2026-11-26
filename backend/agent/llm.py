from langchain_groq import ChatGroq
from backend.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    missing_settings,
)

def get_llm():

    missing = missing_settings("GROQ_API_KEY", "GROQ_MODEL")
    if missing:
        raise RuntimeError(
            "Missing AI configuration: " + ", ".join(missing)
            + ". Add these values to your .env file."
        )

    # Initialising the Groq model.
    llm=ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0
    )

    return llm
