"""FPE File handler interface.

Protocol class that defines the file handler interface.

"""

import pathlib
from typing import Protocol


class IHandler(Protocol):
    """Interface for watcher file handler."""

    name: str = ""
    source: str = ""
    recursive: bool = False
    exit_on_failure: bool = False
    delete_source: bool = True
    files_processed: int = 0
    errors: int = 0

    def process(self, source_path: pathlib.Path) -> bool:
        """Perform watcher file processing.

        Args:
            source_path (pathlib.Path): Source fiel path.
        """

    def status(self) -> str:
        """Return current handler status string

        Returns:
            str: Handler status string.
        """
