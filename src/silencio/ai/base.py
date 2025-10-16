# src/silencio/ai/base.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Protocol

Role = Literal["system", "user", "assistant"]


@dataclass
class ChatMessage:
    role: Role
    content: str


class ChatClient(Protocol):
    """
    A protocol for chat clients that can generate text completions based on a list of chat messages.
    """

    def complete(self, messages: List[ChatMessage]) -> str: ...
