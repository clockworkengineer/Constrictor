"""FPE file watcher consumer interface.

Protocol class that defines the watcher consumer interface.

"""

from typing import Protocol


class IConsumer(Protocol):
    """Interface for watcher consumer."""

    def start(self) -> None:
        """Start consumer."""

    def stop(self) -> None:
        """Stop consumer."""
