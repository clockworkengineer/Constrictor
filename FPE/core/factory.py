"""FPE Watcher handler factory.

Watcher handlers are registered/unregistered and mapped from their string
name to the correct handler function by this factory class.

"""

from typing import Callable

from core.constants import CONFIG_TYPE
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.error import FPEError


class FactoryError(FPEError):
    """An error occurred in the watcher handler factory."""

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """
        return FPEError.error_prefix("Factory") + self.error


class Factory:
    """Factory to create watcher handlers."""

    # Watcher handler creation function dictionary

    __handler_creation_funcs: dict[str, Callable[..., IHandler]] = {}

    @staticmethod
    def register(handler_type: str, handler_fn: Callable[..., IHandler]) -> None:
        """Register a new watcher handler type.

        Args:
            handler_type (str): Watch handler type.
            handler_fn (Callable[..., Handler]): Watch handler.

        Raises:
            FactoryError: An error occurred whilst trying to use watcher factory.
        """

        if handler_type == "":
            raise FactoryError('Invalid handler type ("").')

        if handler_fn is None:
            raise FactoryError("None not allowed for handler function.")

        Factory.__handler_creation_funcs[handler_type] = handler_fn

    @staticmethod
    def unregister(handler_type: str) -> None:
        """Unregister a watcher handler type.

        Args:
            handler_type (str): Watch handler type.

        Raises:
            FactoryError: An error occurred whilst trying to use watcher factory.
        """
        if handler_type not in Factory.__handler_creation_funcs:
            raise FactoryError("Cannot unregister handler not in factory.")

        Factory.__handler_creation_funcs.pop(handler_type, None)

    @staticmethod
    def create(handler_config: ConfigDict) -> IHandler:
        """Create a watcher handler of a specific type given JSON data.

        Args:
            handler_config (ConfigDict): Watcher handler config

        Raises:
            FactoryError: An error occurred whilst trying to use watcher factory.

        Returns:
            Handler: Watch handler.
        """

        if len(Factory.__handler_creation_funcs) == 0:
            raise FactoryError("Factory does not contain any registered handlers.")

        handler_type = handler_config[CONFIG_TYPE]
        try:
            creator_func = Factory.__handler_creation_funcs[handler_type]
        except KeyError as error:
            raise FactoryError(f"Unknown handler type '{handler_type}'.") from error

        return creator_func(handler_config)

    @staticmethod
    def handler_function_list() -> list[str]:
        """Return list of all current watch handler types.

        Returns:
            list[str]: List of watch handler types.
        """
        return list(Factory.__handler_creation_funcs.keys())

    @staticmethod
    def clear() -> None:
        """Clear watch handler type list."""
        Factory.__handler_creation_funcs.clear()
