# src/silencio/settings.py
from __future__ import annotations
import os


def get_openai_api_key() -> str:
    """
    Retrieve the OpenAI API key from environment variables.

    Looks for the 'OPENAI_API_KEY' environment variable and returns its value.
    Raises a ValueError if the key is not set, as it is required for API access.

    Returns:
        The OpenAI API key as a string.

    Raises:
        ValueError: If the 'OPENAI_API_KEY' environment variable is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    return api_key


def get_model_name() -> str:
    """
    Retrieve the OpenAI model name from environment variables, with a default fallback.

    Checks for the 'MODEL_NAME' environment variable. If not set, defaults to 'gpt-5-mini'.
    This allows users to specify a custom model for the redaction process.

    Returns:
        The name of the OpenAI model to use.
    """
    return os.getenv("MODEL_NAME", "gpt-5-mini")
