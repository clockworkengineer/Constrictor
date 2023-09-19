"""FPE file consumer interface.

Protocol class that defines the directory/file consumer interface.

"""

from typing import Protocol


class IConsumer(Protocol):
    """Interface for watcher file consumer."""

    def start(self) -> None:
        """Start consumer."""

    def stop(self) -> None:
        """Stop consumer."""
