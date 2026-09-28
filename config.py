import os

from dotenv import load_dotenv


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# OPENAI SETTINGS
# =====================================================

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna"
)

OPENAI_TIMEOUT = float(
    os.getenv(
        "OPENAI_TIMEOUT",
        "60"
    )
)

OPENAI_MAX_RETRIES = int(
    os.getenv(
        "OPENAI_MAX_RETRIES",
        "2"
    )
)


# =====================================================
# RAG SETTINGS
# =====================================================

CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        "500"
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        "50"
    )
)

DEFAULT_TOP_K = int(
    os.getenv(
        "DEFAULT_TOP_K",
        "3"
    )
)


# =====================================================
# API KEY
# =====================================================

def get_api_key():
    """
    Get the OpenAI API key
    from environment variables.
    """

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. "
            "Please add it to your environment variables."
        )

    return api_key