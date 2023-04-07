"""Watcher file handler.
"""


from core.error import FPEError


class Handler(FPEError):
    """Watcher file handler class"""

    handler_config: dict[str, any]

    def process(self, event) -> None:
        """Perform watcher file processing.
        """
