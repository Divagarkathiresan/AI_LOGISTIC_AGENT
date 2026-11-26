from langchain_groq import ChatGroq
from backend.config import (
    GROQ_API_KEY,
    GROQ_MODEL
)

def get_llm():

    #initialising the groq model
    llm=ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0
    )
    
    return llm

if __name__ == "__main__":
    llm=get_llm()
    response = llm.invoke(
        "Explain what a SQL JOIN is in two sentences."
    )
    print(response.content)
