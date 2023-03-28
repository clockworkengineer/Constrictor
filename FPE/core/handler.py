""" Watcher file handler definitions built-in.
"""

import os

from typing import Protocol


class Handler(Protocol):
    """Watcher file handler class"""

    def process(self, event):
        """Perform watcher file processing.
        """
