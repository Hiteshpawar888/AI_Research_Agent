import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


def get_api_key():
    """Get the OpenAI API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing.")

    return api_key