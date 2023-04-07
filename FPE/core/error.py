"""FPE base error.
"""


class FPEError(Exception):
    """An error occured in the FPE.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "FPE Error: " + str(self.message)
