# src/silencio/core/chat.py
from __future__ import annotations
from typing import List, Optional
from ..ai.base import ChatMessage
from ..ai.openai_client import OpenAIChatClient

DEFAULT_SYSTEM = "You are a concise data analyst assistance. Reply directly."


def simple_roundtrip(user_text: str, system_prompt: Optional[str] = None) -> str:
    """
    Perform a simple roundtrip chat interaction with the AI model.

    Sends a system prompt (defaulting to a concise data analyst assistant) and the user's text
    to the OpenAI chat client, then returns the model's response. This is a basic wrapper for
    single-turn conversations.

    Args:
        user_text: The user's input message.
        system_prompt: Optional system prompt to set the AI's behavior. Defaults to a standard prompt.

    Returns:
        The AI model's response as a string.
    """
    client = OpenAIChatClient()
    messages: List[ChatMessage] = [
        ChatMessage(role="system", content=system_prompt or DEFAULT_SYSTEM),
        ChatMessage(role="user", content=user_text),
    ]
    return client.complete(messages)
