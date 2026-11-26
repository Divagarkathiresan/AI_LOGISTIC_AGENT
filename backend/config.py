
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

def missing_settings(*names: str) -> list[str]:
    """Return missing settings when a component is actually used.

    Keeping validation lazy means schema/validator tests and Streamlit's
    startup page can load even before the developer has created `.env`.
    """
    settings = globals()
    return [name for name in names if not settings.get(name)]
