"""Watcher handler factory.
"""

from typing import Any, Callable
from .handler import Handler


class FactoryError(Exception):
    """An error occured in the watcher handler factory.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "Factory Error: " + str(self.message)


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
        """Create a watcher handler of a specific type, given JSON data.
        """

        handler_type = arguments["type"]
        try:
            creator_func = Factory.handler_creation_funcs[handler_type]
        except KeyError as error:
            raise FactoryError(
                f"Unknown handler type '{handler_type}'") from error

        return creator_func(arguments)
