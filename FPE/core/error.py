"""FPE base error.
"""

from core.constants import APP_NAME


class FPEError(Exception):
    """An error occurred in the FPE.
    """

    @staticmethod
    def error_prefix(component: str) -> str:
        """_summary_

        Args:
            component (str): _description_

        Returns:
            str: _description_
        """
        return APP_NAME+component+": "
