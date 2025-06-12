from typing import Protocol
from dotenv import load_dotenv


class AIProvider(Protocol):
    """Minimal interface for interacting with AI providers in a consistent manner."""

    async def chat(self, prompt: str) -> str: ...


# Registry for available providers
_providers: dict[str, "AIProvider"] = {}


def register_provider(name: str, provider: "AIProvider") -> None:
    _providers[name] = provider


def get_provider(name: str) -> "AIProvider":
    try:
        return _providers[name]
    except KeyError:  # pragma: no cover
        raise ValueError(f"Provider '{name}' is not registered. Available: {list(_providers)}")


# Import providers for side-effect registration.
load_dotenv()
from . import openai_provider  # noqa: F401
from . import gemini_provider  # noqa: F401 