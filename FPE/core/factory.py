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

    _handler_creation_funcs: dict[str, Callable[..., Handler]] = {}

    @staticmethod
    def register(handler_type: str, handler_fn: Callable[..., Handler]) -> None:
        """Register a new watcher handler type.
        """

        if handler_type == "":
            raise FactoryError("Invalid handler type (\"\").")

        if handler_fn == None:
            raise FactoryError("None not allowed for handler function.")

        Factory._handler_creation_funcs[handler_type] = handler_fn

    @staticmethod
    def unregister(handler_type: str) -> None:
        """Unregister a watcher handler type.
        """
        if handler_type not in Factory._handler_creation_funcs:
            raise FactoryError(
                "Cannot unregiester handler not in factory.")

        Factory._handler_creation_funcs.pop(handler_type, None)

    @staticmethod
    def create(arguments: dict[str, Any]) -> Handler:
        """Create a watcher handler of a specific type given JSON data.
        """

        if len(Factory._handler_creation_funcs) == 0:
            raise FactoryError(
                "Factory does not contain any registered handlers.")

        handler_type = arguments["type"]
        try:
            creator_func = Factory._handler_creation_funcs[handler_type]
        except KeyError as error:
            raise FactoryError(
                f"Unknown handler type '{handler_type}'.") from error

        return creator_func(arguments)
    

    @staticmethod
    def handler_function_list() -> list[str]:
        return list(Factory._handler_creation_funcs.keys())
    
    @staticmethod
    def clear() -> None:
        Factory._handler_creation_funcs.clear()
