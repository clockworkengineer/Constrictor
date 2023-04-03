"""Watcher file handler.
"""

from typing import Protocol


class Handler(Protocol):
    """Watcher file handler class"""

    handler_config : dict[str, any]
    
    def process(self, event) -> None:
        """Perform watcher file processing.
        """
