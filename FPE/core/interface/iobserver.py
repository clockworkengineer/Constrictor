"""FPE File observer interface.

Protocol class that defines the directory/file observer interface.

"""

import pathlib
from typing import Protocol

from core.config import ConfigDict


class IObserver(Protocol):
    """Interface for watcher file handler.
    """

    def start(self) -> None:
        """Start observer.
        """
        ...

    def stop(self) -> None:
        """Stop observer.
        """
        ...
