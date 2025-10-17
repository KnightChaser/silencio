# src/silencio/settings.py
from __future__ import annotations
import os


def get_openai_api_key() -> str:
    """
    Retrieve the OpenAI API key from environment variables.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    return api_key


def get_model_name() -> str:
    """
    Retrieve the model name from environment variables or use a default.
    """
    return os.getenv("MODEL_NAME", "gpt-5-mini")
