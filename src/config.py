from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    # --- Project Info ---
    APP_NAME: str = "Security Scanner"
    VERSION: str = "0.1.0"
    
    # --- The Brain Selector ---
    LLM_PROVIDER: Literal["openai", "ollama", "google"] = "ollama"

    # --- Provider Specifics ---

    # 1. Google Gemini (Free Tier available)
    GOOGLE_API_KEY: str | None = None
    GOOGLE_MODEL: str = "gemini-1.5-flash"

    # 2. Ollama (Local & Free)
    # The URL where Ollama is running (usually localhost:11434)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3" 

    # 3. OpenAI (Paid)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"

    # --- Scanner Settings ---
    MAX_CONCURRENCY: int = 5
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()