from pathlib import Path
import os

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Settings:
    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAIAPIKEY")
        self.scrapegraphai_api_key = os.getenv("SCRAPEGRAPHAI_API_KEY")
        self.scrapegraphai_base_url = os.getenv("SCRAPEGRAPHAI_BASE_URL")
        self.supabase_db_pwd = os.getenv("SUPABASE_DB_PWD")
        self.supabase_url = os.getenv("SUPABASE_URL_BIZ")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY_BIZ")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY_BIZ")
        self.openai_llm = os.getenv("OPENAI_LLM", "gpt-4.1-mini")
        self.openai_embedding_model = os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        )
        self.job_urls_file = str((BACKEND_DIR.parent / "job_urls.txt").resolve())
        self.default_recommendation_count = int(os.getenv("DEFAULT_RECOMMENDATION_COUNT", "10"))
        self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()

# Backward-compatible exports for existing imports.
OPENAIAPIKEY = settings.openai_api_key
SCRAPEGRAPHAI_API_KEY = settings.scrapegraphai_api_key
SCRAPEGRAPHAI_BASE_URL = settings.scrapegraphai_base_url
SUPABASE_DB_PWD = settings.supabase_db_pwd
SUPABASE_URL_BIZ = settings.supabase_url
SUPABASE_ANON_KEY_BIZ = settings.supabase_anon_key
SUPABASE_SERVICE_KEY_BIZ = settings.supabase_service_key
OPENAI_LLM = settings.openai_llm
OPENAI_EMBEDDING_MODEL = settings.openai_embedding_model
