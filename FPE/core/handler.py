"""Watcher file handler protocol class.
"""

from typing import Protocol


class Handler(Protocol):
    """Watcher file handler class"""

    def process(self, event) -> None:
        """Perform watcher file processing.
        """
