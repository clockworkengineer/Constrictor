"""Watcher handler factory.
"""

from typing import Any, Callable
from .handler import Handler


class FactoryError(Exception):
    """An error occured in the FPE watcher handler factory.
    """


class Factory:
    """Factory to create watcher handlers.
    """

    # Watcher handler creation function dictionary

    handler_creation_funcs: dict[str, Callable[..., Handler]] = {}

    @staticmethod
    def register(handler_type: str, handler_fn: Callable[..., Handler]) -> None:
        """Register a new watcher handler type.
        """
        Factory.handler_creation_funcs[handler_type] = handler_fn

    @staticmethod
    def unregister(handler_type: str) -> None:
        """Unregister a watcher handler type."""
        Factory.handler_creation_funcs.pop(handler_type, None)

    @staticmethod
    def create(arguments: dict[str, Any]) -> Handler:
        """Create a watcher handler of a specific type, given JSON data.
        """
        args_copy = arguments.copy()
        handler_type = args_copy.pop("type")
        try:
            creator_func = Factory.handler_creation_funcs[handler_type]
        except KeyError:
            raise FactoryError(
                f"unknown handler type {handler_type!r}") from None
        return creator_func(args_copy)
