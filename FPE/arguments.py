""" Argument handling code.
"""

import sys
import os
import argparse


def load_arguments() -> argparse.Namespace:
    """Load and parse command line arguments
    """

    parser = argparse.ArgumentParser(
        description="Process files copied into watch folder with a custom handler(s).")
    parser.add_argument("file", help="Configuration file")

    arguments = parser.parse_args()

    if not os.path.exists(arguments.file):
        print("Error: Non-existent config file passed to FPE.")
        sys.exit(1)

    return arguments
