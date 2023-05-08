"""FPE base error.
"""


class FPEError(Exception):
    """An error occurred in the FPE.
    """

    @staticmethod
    def error_prefix(component: str) -> str:
        return "FPE"+component+": "
