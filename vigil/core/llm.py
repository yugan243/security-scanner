from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from vigil.config import settings
import logging

logger = logging.getLogger(settings.APP_NAME)

def get_llm():
    """
    Factory function that returns the configured LLM based on settings.
    """
    provider = settings.LLM_PROVIDER
    logger.info(f"Initializing LLM Provider: {provider}")

    # 1. Google Gemini (Cloud - Free Tier)
    if provider == "google":
        if not settings.GOOGLE_API_KEY:
            raise ValueError("LLM_PROVIDER is 'google' but GOOGLE_API_KEY is missing in .env")
        
        return ChatGoogleGenerativeAI(
            model=settings.GOOGLE_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,  # Deterministic output for security scans
            convert_system_message_to_human=True # Fix for Gemini distinct roles
        )

    # 2. Ollama (Local - Free)
    elif provider == "ollama":
        # Ollama is compatible with the OpenAI API format!
        return ChatOpenAI(
            base_url=f"{settings.OLLAMA_BASE_URL}/v1",
            api_key="ollama",  # Ollama doesn't need a real key, but the client requires a string
            model=settings.OLLAMA_MODEL,
            temperature=0
        )

    # 3. OpenAI (Cloud - Paid)
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("LLM_PROVIDER is 'openai' but OPENAI_API_KEY is missing in .env")
            
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0
        )
    elif provider == "groq":
        if not settings.GROQ_API_KEY:
             raise ValueError("GROQ_API_KEY is missing")
        
        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=0
        )

    else:
        raise ValueError(f"Unsupported LLM Provider: {provider}")

# Usage Test
if __name__ == "__main__":
    try:
        llm = get_llm()
        print(f"Successfully connected to: {settings.LLM_PROVIDER}")
        print("Testing connection...")
        response = llm.invoke("Hello, are you ready to scan for security vulnerabilities?")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Failed to connect: {e}")