import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

KNOWLEDGE_BASE_PATH = BASE_DIR / "data" / "knowledge_base_hometech.csv"


if not OPENAI_API_KEY:
    raise ValueError(
        "Не найден OPENAI_API_KEY. "
        "Добавьте ключ OpenAI API в файл .env"
    )

if not KNOWLEDGE_BASE_PATH.exists():
    raise FileNotFoundError(
        f"Не найдена база знаний: {KNOWLEDGE_BASE_PATH}"
    )