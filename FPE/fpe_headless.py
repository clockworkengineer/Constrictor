"""Run FPE headless.
"""

import logging
import time

from core.engine import Engine


def fpe_headless(fpe_engine: Engine) -> None:
    """Run FPE without a user inerface.

    Args:
        fpe_engine (Engine): FPE control engine.
    """
    try:
        logging.info("Running with no user interface.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("File Processing Engine interrupted...")
