"""Watcher file handler.

Protocol class that defines the file watcher handler interface.

"""


from typing import Protocol


class Handler(Protocol):
    """Watcher file handler class"""

    handler_config: dict[str, any]  # Handler config dictionary

    def process(self, event) -> None:
        """Perform watcher file processing.
        """
