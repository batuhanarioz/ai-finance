import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@localhost:5432/finagent")
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o"
    USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    LOCAL_MODEL_NAME = "trendyol-llm"
    
    # Katılım Bankacılığı Terminolojisi (Architecht/Kuveyt Türk Uyumu)
    BANK_NAME = "Batuhan Bank"
    TERMS = {
        "faiz": "kar payı",
        "kredi": "finansman",
        "mevduat": "katılım hesabı"
    }

settings = Config()
