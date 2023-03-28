"""Watcher file handler.
"""

from typing import Protocol


class Handler(Protocol):
    """Watcher file handler class"""

    def process(self, event):
        """Perform watcher file processing.
        """
