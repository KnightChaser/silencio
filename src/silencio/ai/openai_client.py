# src/silencio/ai/openai_client.py
from __future__ import annotations
from typing import List
from openai import OpenAI
from .base import ChatClient, ChatMessage
from ..settings import get_openai_api_key, get_model_name


class OpenAIChatClient(ChatClient):
    def __init__(self):
        self._client = OpenAI(api_key=get_openai_api_key())
        self._model: str = get_model_name()

    def complete(self, messages: List[ChatMessage]) -> str:
        """
        Generate a completion for the given messages using the OpenAI API.
        """
        response = self._client.responses.create(
            model=self._model,  # type: ignore
            input=[{"role": msg.role, "content": msg.content} for msg in messages],  # type: ignore
        )
        return response.output_text
