"""FPE File observer interface.

Protocol class that defines the directory/file observer interface.

"""

from typing import Protocol


class IObserver(Protocol):
    """Interface for watcher file handler."""

    def start(self) -> None:
        """Start observer."""

    def stop(self) -> None:
        """Stop observer."""
