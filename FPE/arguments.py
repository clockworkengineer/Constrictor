""" Arguments class.
"""

import os
import argparse


class ArgumentsError(Exception):
    """An error occured in the program command line arguments.
    """


class Arguments:
    """Extract arguments from command line and create arguments object.
    """

    def __init__(self) -> None:
        """Load and parse command line into arguments object.
        """

        parser = argparse.ArgumentParser(
            description="Process files copied into watch folder with a custom handler(s).")
        parser.add_argument("file", help="Configuration file")

        arguments = parser.parse_args()

        if not os.path.exists(arguments.file):
            raise ArgumentsError("Non-existent config file passed to FPE.")

        self.file = arguments.file
