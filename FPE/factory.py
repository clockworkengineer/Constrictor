"""Watcher handler factory.
"""

from typing import Any, Callable
from handler import Handler


# """Factory for creating a watcher handler."""


handler_creation_funcs: dict[str, Callable[..., Handler]] = {}


def register(handler_type: str, handler_fn: Callable[..., Handler]) -> None:
    """Register a new watcher handler type."""
    handler_creation_funcs[handler_type] = handler_fn


def unregister(handler_type: str) -> None:
    """Unregister a watcher handler type."""
    handler_creation_funcs.pop(handler_type, None)


def create(arguments: dict[str, Any]) -> Handler:
    """Create a watcher handler of a specific type, given JSON data."""
    args_copy = arguments.copy()
    handler_type = args_copy.pop("type")
    try:
        creator_func = handler_creation_funcs[handler_type]
    except KeyError:
        raise ValueError(f"unknown handler type {handler_type!r}") from None
    return creator_func(args_copy)
