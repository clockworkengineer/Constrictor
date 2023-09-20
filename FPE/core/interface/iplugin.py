"""FPE plug-in interface.

Protocol class that defines the file watcher handler plugin interface.

"""
from typing import Protocol


class IPlugin(Protocol):
    """Plug-in interface."""

    def register(self) -> None:
        """Register the necessary items in the watcher handler factory."""
