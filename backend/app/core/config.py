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

def save_settings_to_env(updates: dict):
    """
    Persists configuration updates into backend/.env and updates
    in-memory settings and os.environ immediately without restarting the server.
    """
    env_path = base_dir / ".env"
    existing_lines = []
    if env_path.exists():
        existing_lines = env_path.read_text(encoding="utf-8").splitlines()

    key_found = set()
    new_lines = []

    for line in existing_lines:
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("#"):
            new_lines.append(line)
            continue
        if "=" in line:
            k, _ = line.split("=", 1)
            k = k.strip()
            if k in updates:
                new_lines.append(f"{k}={updates[k]}")
                key_found.add(k)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    for k, v in updates.items():
        if k not in key_found:
            new_lines.append(f"{k}={v}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    for k, v in updates.items():
        os.environ[k] = str(v)
        if hasattr(settings, k):
            setattr(settings, k, str(v))
