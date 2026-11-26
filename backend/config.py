
import os
from pathlib import Path
from dotenv import load_dotenv

# Find project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL=os.getenv("GROQ_MODEL")

# Validate configuration
required_variables = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_NAME": DB_NAME,
    "GROQ_API_KEY":GROQ_API_KEY,
    "GROQ_MODEL":GROQ_MODEL
}

missing = [
    key for key, value in required_variables.items()
    if not value
]

if missing:
    raise ValueError(
        f"Missing environment variables: {missing}"
    )
