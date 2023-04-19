"""Watcher file handler.

Protocol class that defines the file watcher handler interface.

"""

import os
from typing import Protocol, Any


class Handler(Protocol):
    """Watcher file handler class"""

    handler_config: dict[str, Any]  # Handler config dictionary

    def process(self, source_path: str) -> None:
        """Perform watcher file processing.
        """

    @staticmethod
    def normalize_path(path: str):
        return os.path.join(path, '')
