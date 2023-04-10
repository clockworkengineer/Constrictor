"""Watcher handler factory.

Watcher handlers are registered/unregistered and mapped from their string
name to the correct handler function by this factory class.

"""

from typing import Any, Callable

from core.handler import Handler
from core.error import FPEError


class FactoryError(FPEError):
    """An error occurred in the watcher handler factory.
    """

    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return "FPE Factory Error: " + str(self.message)


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
        """Unregister a watcher handler type.
        """
        Factory.handler_creation_funcs.pop(handler_type, None)

    @staticmethod
    def create(arguments: dict[str, Any]) -> Handler:
        """Create a watcher handler of a specific type given JSON data.
        """
        handler_type = arguments["type"]
        try:
            creator_func = Factory.handler_creation_funcs[handler_type]
        except KeyError as error:
            raise FactoryError(
                f"Unknown handler type '{handler_type}'.") from error

        return creator_func(arguments)
