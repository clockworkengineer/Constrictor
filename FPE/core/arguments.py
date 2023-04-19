""" Arguments class.

Convert command line arguments into an object that can be accessed by the FPE.
Performing any validation required on the passed in parameters and generating
any exceptions for any errors found. This is currently just a JSON configuration
file that is used to specify any custom plugins and running handler details.

"""

import pathlib
import argparse

from core.error import FPEError


class ArgumentsError(FPEError):
    """An error occurred in the program command line arguments.
    """

    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return "FPE Arguments Error: " + str(self.message)


class Arguments:
    """Extract arguments from command line and create arguments object.
    """

    # Parsed argument attributes

    file: str   # Configuration file name

    def __init__(self, argv=None) -> None:
        """Load and parse command line into arguments object.
        """
        
        # Extract and parse arguments

        parser = argparse.ArgumentParser(
            description="Process files copied into watch folder with a custom handler(s).")
        parser.add_argument("file", help="Configuration file")
        
        arguments = parser.parse_args(argv)

        # Check that configuration file exists

        if not pathlib.Path(arguments.file).exists():
            raise ArgumentsError("Non-existent config file passed to FPE")

        # Pass back valid attributes

        self.file = arguments.file
