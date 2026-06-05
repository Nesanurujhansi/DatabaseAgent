import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class to manage API keys and system settings.
    """
    # API Key for Google Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # AI Model Version
    MODEL_NAME = "gemini-3.5-flash"
    
    # System Instruction for the Bot
    SYSTEM_INSTRUCTION = (
        "You are a helpful, professional, and friendly AI chatbot. "
        "Keep your responses concise and engaging."
    )

    # Database Settings (Hardened Read-Only defaults for AI runtime)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "readonly_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "readonly_pass")
    DB_NAME = os.getenv("DB_NAME", "customerss")
    DB_PORT = os.getenv("DB_PORT", "3306")

    @staticmethod
    def validate_config():
        """
        Validates that all necessary configuration variables are present.
        """
        if not Config.GEMINI_API_KEY:
            raise ValueError(
                "Missing GEMINI_API_KEY. Please ensure it is set in your environment variables or .env file."
            )
