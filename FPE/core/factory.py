"""Watcher handler factory.

Watcher handlers are registered/unregistered and mapped from their string
name to the correct handler function by this factory class.

"""

from typing import Any, Callable
from typing import Any

from core.handler import Handler
from core.error import FPEError


class FactoryError(FPEError):
    """An error occurred in the watcher handler factory.
    """

    def __init__(self, message: Any) -> None:
        """Create factory exception.

        Args:
            message (str): Exception message.
        """
        self.message = message

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """
        return FPEError.error_prefix("Factory") + str(self.message)


class Factory:
    """Factory to create watcher handlers.
    """

    # Watcher handler creation function dictionary

    _handler_creation_funcs: dict[str, Callable[..., Handler]] = {}

    @ staticmethod
    def register(handler_type: str, handler_fn: Callable[..., Handler]) -> None:
        """"Register a new watcher handler type.

        Args:
            handler_type (str): Watch handler type.
            handler_fn (Callable[..., Handler]): Watch handler.

        Raises:
            FactoryError: An error occured whilst tryinhg to use watcher factory.
        """

        if handler_type == "":
            raise FactoryError("Invalid handler type (\"\").")

        if handler_fn == None:
            raise FactoryError("None not allowed for handler function.")

        Factory._handler_creation_funcs[handler_type] = handler_fn

    @ staticmethod
    def unregister(handler_type: str) -> None:
        """Unregister a watcher handler type.

        Args:
            handler_type (str): Watch handler type.

        Raises:
            FactoryError: An error occured whilst tryinhg to use watcher factory.
        """
        if handler_type not in Factory._handler_creation_funcs:
            raise FactoryError(
                "Cannot unregiester handler not in factory.")

        Factory._handler_creation_funcs.pop(handler_type, None)

    @ staticmethod
    def create(handler_config: dict[str, Any]) -> Handler:
        """Create a watcher handler of a specific type given JSON data.

        Args:
            handler_config (dict[str, Any]): Watcher handler config

        Raises:
            FactoryError: An error occured whilst tryinhg to use watcher factory.

        Returns:
            Handler: Watch handler.
        """

        if len(Factory._handler_creation_funcs) == 0:
            raise FactoryError(
                "Factory does not contain any registered handlers.")

        handler_type = handler_config["type"]
        try:
            creator_func = Factory._handler_creation_funcs[handler_type]
        except KeyError as error:
            raise FactoryError(
                f"Unknown handler type '{handler_type}'.") from error

        return creator_func(handler_config)

    @ staticmethod
    def handler_function_list() -> list[str]:
        """Return list of all current watch handler types.

        Returns:
            list[str]: List of watch handler types.
        """
        return list(Factory._handler_creation_funcs.keys())

    @ staticmethod
    def clear() -> None:
        """Clear watch handler type list.
        """
        Factory._handler_creation_funcs.clear()
