"""FPE File handler interface.

Protocol class that defines the file handler interface.

"""

import pathlib
from typing import Protocol

from core.config import ConfigDict


class IHandler(Protocol):
    """Interface for watcher file handler.
    """

    source: str
    destination: str
    recursive: str
    exitonfailure: bool
    deletesource: bool
    files_processed : int

    def process(self, source_path: pathlib.Path) -> bool:
        """Perform watcher file processing.

        Args:
            source_path (pathlib.Path): Source fiel path.
        """
        ...
