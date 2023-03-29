""" Arguments class.

Convert command line arguments into an object that can be accessed by the FPE.
Performing any validation required on the passed in parameters and generating
any exceptions for any errors found.

"""

import os
import argparse


class ArgumentsError(Exception):
    """An error occured in the program command line arguments.
    """


class Arguments:
    """Extract arguments from command line and create arguments object.
    """

    file : str = "" # Configuration file name
    
    def __init__(self) -> None:
        """Load and parse command line into arguments object.
        """

        # Extract and parse arguments
        
        parser = argparse.ArgumentParser(
            description="Process files copied into watch folder with a custom handler(s).")
        parser.add_argument("file", help="Configuration file")

        arguments = parser.parse_args()

        # Check that configuration file exists

        if not os.path.exists(arguments.file):
            raise ArgumentsError("Non-existent config file passed to FPE.")

        # Pass back valid parameters
        
        self.file = arguments.file
