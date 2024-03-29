"""FPE file watcher observer interface.

Protocol class that defines the directory/file watcher observer interface.

"""

from typing import Protocol


class IObserver(Protocol):
    """Interface for watcher file observer."""

    def start(self) -> None:
        """Start observer."""

    def stop(self) -> None:
        """Stop observer."""
