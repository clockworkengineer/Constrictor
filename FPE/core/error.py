"""FPE base error.
"""
from typing import Any

from core.constants import APP_NAME


class FPEError(Exception):
    """An error occurred in the FPE."""

    def __init__(self, error: Any) -> None:
        """CopyFileHandler error.

        Args:
            error (Any): Exception.
        """
        self.error = error

    @staticmethod
    def error_prefix(component: str) -> str:
        """Prefix application name and component to passed in string.

        Args:
            component (str): Component name

        Returns:
            str: String with application name plus component.
        """
        return APP_NAME + component + ": "
