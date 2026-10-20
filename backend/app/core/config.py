import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from backend directory or project root
base_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(base_dir / ".env")
load_dotenv(base_dir.parent / ".env")

class Settings(BaseModel):
    PROJECT_NAME: str = "Noto API"
    VERSION: str = "0.1.0"
    
    # Storage
    DATA_DIR: Path = base_dir.parent / "data"
    DATABASE_PATH: Path = DATA_DIR / "noto.db"
    
    # AI Providers
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "gemini")  # "gemini" or "ollama"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
