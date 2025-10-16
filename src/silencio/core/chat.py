# src/silencio/core/chat.py
from __future__ import annotations
from typing import List, Optional
from ..ai.base import ChatMessage
from ..ai.openai_client import OpenAIChatClient

DEFAULT_SYSTEM = "You are a concise data analyst assistance. Reply directly."


def simple_roundtrip(user_text: str, system_prompt: Optional[str] = None) -> str:
    """
    Perform a simple roundtrip chat interaction with the AI model.
    """
    client = OpenAIChatClient()
    messages: List[ChatMessage] = [
        ChatMessage(role="system", content=system_prompt or DEFAULT_SYSTEM),
        ChatMessage(role="user", content=user_text),
    ]
    return client.complete(messages)
