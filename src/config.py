from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

# Vigil config lives in the user's home directory
VIGIL_CONFIG_DIR = Path.home() / ".vigil"
VIGIL_ENV_FILE = VIGIL_CONFIG_DIR / ".env"

class Settings(BaseSettings):
    # --- Project Info ---
    APP_NAME: str = "Vigil"
    VERSION: str = "0.1.0"
    
    # --- The Brain Selector ---
    LLM_PROVIDER: Literal["openai", "ollama", "google", "groq"] = "ollama"

    # --- Provider Specifics ---

    # 1. Google Gemini (Free Tier available)
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_MODEL: str = "gemini-2.5-flash"

    # 2. Ollama (Local & Free)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3" 

    # 3. OpenAI (Paid)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    # 4. Groq (Free)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # --- Scanner Settings ---
    MAX_CONCURRENCY: int = 5

    # --- Optional (dev/benchmark only) ---
    hf_token: Optional[str] = None
    
    # Load config from: ~/.vigil/.env first, then project .env (dev override)
    # Environment variables always take highest priority (for Docker/CI)
    model_config = SettingsConfigDict(
        env_file=(str(VIGIL_ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

def reload_settings():
    """Reload settings after configuration changes (e.g., after vigil init)."""
    global settings
    settings = Settings()