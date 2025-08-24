from typing import Type

# Important: Import all handler modules here so the @register_handler decorator runs
from . import france_messagerie_handler as france_messagerie  # noqa: F401
from . import mlp_handler as mlp  # noqa: F401
from .base_handler import HANDLER_REGISTRY, BaseHandler


def get_handler_for_provider(provider_id: str) -> Type[BaseHandler]:
    """
    Factory that returns the appropriate Handler CLASS for a given provider ID.
    """
    HandlerClass = HANDLER_REGISTRY.get(provider_id)
    if not HandlerClass:
        raise NotImplementedError(f'No handler has been registered for provider ID: {provider_id}')
    return HandlerClass
