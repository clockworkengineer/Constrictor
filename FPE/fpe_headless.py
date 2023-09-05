"""Run FPE headless.
"""

import logging
import time


def fpe_headless() -> None:
    """Run FPE without a user interface."""
    try:
        logging.info("Running with no user interface.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("File Processing Engine interrupted...")
