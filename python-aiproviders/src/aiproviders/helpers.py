from typing import Any, cast

from providerkit.helpers import call_providers, get_providers

from .providers import AIProviderBase


def get_ai_providers(*args: Any, **kwargs: Any) -> dict[str, Any] | str:
    """Get AI providers."""
    lib_name = kwargs.pop('lib_name', 'aiproviders')
    return cast('dict[str, Any] | str', get_providers(*args, lib_name=lib_name, **kwargs))


def get_ai_provider(attribute_search: dict[str, Any], *args: Any, **kwargs: Any) -> AIProviderBase:
    """Get AI provider by attribute search."""
    lib_name = kwargs.pop('lib_name', 'aiproviders')
    providers = get_providers(*args, attribute_search=attribute_search, format="python", lib_name=lib_name, **kwargs)
    if not providers:
        raise ValueError("No providers found")
    if len(providers) > 1:
        raise ValueError(f"Expected 1 provider, got {len(providers)}")
    return cast('AIProviderBase', providers[0])


def prompt(instruction: str, *args: Any, **kwargs: Any) -> Any:
    """Run prompt (agent loop) using AI providers."""
    return call_providers(
        *args,
        command="prompt",
        lib_name="aiproviders",
        instruction=instruction,
        **kwargs,
    )


def get_models(*args: Any, **kwargs: Any) -> Any:
    """List LLM models from AI providers."""
    return call_providers(
        *args,
        command="get_models",
        lib_name="aiproviders",
        **kwargs,
    )
