"""Create file event handler object.
  
Factory function create_watcher used to create a file watcher object
from the watcher config data passed in. These watchers are then passed into 
a watchdog observer specially created for it and used to process files passed
to handler method on_created().

"""

import logging
import builtin_handlers


def create_watcher(watcher_config):
    """Generate watchdog event handler object for the watcher configuration passed in."""

    file_handler = None

    try:

        handler_class = getattr(builtin_handlers, watcher_config['type'])
        file_handler = handler_class(watcher_config)

    except KeyError as e:
        logging.error("Missing option {}.\n{} not started.".format(
            e, watcher_config['name']))
    except AttributeError:
        logging.error('Invalid file handler type [{type}].\n{name} not started.'.format(
            **watcher_config))

    return file_handler

# """Factory for creating a handler character."""

# from typing import Any, Callable

# from game.character import GameCharacter

# character_creation_funcs: dict[str, Callable[..., GameCharacter]] = {}


# def register(character_type: str, creator_fn: Callable[..., GameCharacter]) -> None:
#     """Register a new game character type."""
#     character_creation_funcs[character_type] = creator_fn


# def unregister(character_type: str) -> None:
#     """Unregister a game character type."""
#     character_creation_funcs.pop(character_type, None)


# def create(arguments: dict[str, Any]) -> GameCharacter:
#     """Create a game character of a specific type, given JSON data."""
#     args_copy = arguments.copy()
#     character_type = args_copy.pop("type")
#     try:
#         creator_func = character_creation_funcs[character_type]
#     except KeyError:
#         raise ValueError(f"unknown character type {character_type!r}") from None
#     return creator_func(**args_copy)
