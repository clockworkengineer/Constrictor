"""FPE base error.
"""

from core.constants import APP_NAME

class FPEError(Exception):
    """An error occurred in the FPE.
    """

    @staticmethod
    def error_prefix(component: str) -> str:
        return APP_NAME+component+": "
