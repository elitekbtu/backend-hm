import os
import asyncio
from typing import Any

import google.generativeai as genai

from . import register_provider, AIProvider


class GeminiProvider(AIProvider):
    def __init__(self, model: str = "gemini-1.5-flash") -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # error will be raised later on use
            genai.configure()
        else:
            genai.configure(api_key=api_key)

        self._api_key = api_key or ""
        self._model_name = model
        # create model instance lazily due to potential patching in library
        self._model: Any | None = None

    def _ensure_model(self) -> Any:
        if self._model is None:
            # GenerativeModel constructor may raise if model id invalid
            self._model = genai.GenerativeModel(self._model_name)
        return self._model

    async def chat(self, prompt: str) -> str:
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set on server.")

        model = self._ensure_model()

        # generate_content is blocking; run in thread executor
        def _generate() -> str:
            resp = model.generate_content(prompt)
            # The response object has 'text' attribute in current versions.
            return getattr(resp, "text", str(resp))

        return await asyncio.to_thread(_generate)


register_provider("gemini", GeminiProvider()) 