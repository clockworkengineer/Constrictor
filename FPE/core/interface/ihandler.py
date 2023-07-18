"""FPE File handler interface.

Protocol class that defines the file handler interface.

"""

import pathlib
from typing import Protocol


class IHandler(Protocol):
    """Interface for watcher file handler.
    """

    source: str = ""
    destination: str = ""
    recursive: bool = False
    exitonfailure: bool = False
    deletesource: bool = True
    files_processed: int = 0

    def process(self, source_path: pathlib.Path) -> bool:
        """Perform watcher file processing.

        Args:
            source_path (pathlib.Path): Source fiel path.
        """
