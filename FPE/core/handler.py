"""Watcher file handler.

Protocol class that defines the file watcher handler interface.

"""

import pathlib
from typing import Protocol, Any


class Handler(Protocol):
    """Watcher file handler class"""

    handler_config: dict[str, Any]  # Handler config dictionary

    def process(self, source_path: str) -> None:
        """Perform watcher file processing.
        """

    @staticmethod
    def normalize_path(path: str):
        path = str(pathlib.Path(path).resolve())
