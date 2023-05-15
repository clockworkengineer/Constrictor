"""File handler interface.

Protocol class that defines the file handler interface.

"""

import pathlib
from typing import Protocol, Any

from core.config import ConfigDict


class IHandler(Protocol):
    """Interface for watcher file handler.
    """

    handler_config: ConfigDict  # Handler config dictionary

    def process(self, source_path: pathlib.Path) -> None:
        """Perform watcher file processing.

        Args:
            source_path (pathlib.Path): Source fiel path.
        """
