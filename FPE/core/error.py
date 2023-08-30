"""FPE base error.
"""

from core.constants import APP_NAME


class FPEError(Exception):
    """An error occurred in the FPE.
    """

    def __init__(self, message) -> None:
        """CopyFileHandler error.

        Args:
            message (str): Exception message.
        """
        
        self.message = message
        
    @staticmethod
    def error_prefix(component: str) -> str:
        """Prefix application name and component to passed in string.

        Args:
            component (str): Component name

        Returns:
            str: String with application name plus component.
        """
        return APP_NAME+component+": "
