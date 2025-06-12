import os
import asyncio
from typing import Any
import functools

import openai

from . import register_provider, AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        # store key and defer client construction until first request
        self._api_key = api_key or ""
        self._client: openai.OpenAI | None = None
        self._model = model

    def _ensure_client(self) -> openai.OpenAI:
        if self._client is None:
            if not self._api_key:
                raise RuntimeError("OPENAI_API_KEY environment variable not set on server.")
            self._client = openai.OpenAI(api_key=self._api_key)
        return self._client

    async def chat(self, prompt: str) -> str:
        """Send chat completion request in a thread to keep event loop free."""
        client = self._ensure_client()

        completion: Any = await asyncio.to_thread(
            functools.partial(
                client.chat.completions.create,
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
        )
        return completion.choices[0].message.content


# register on import
register_provider("openai", OpenAIProvider()) 