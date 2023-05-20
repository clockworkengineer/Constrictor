import logging
import time

from core.engine import Engine

def fpe_headerless(fpe_engine:Engine):

    try:
        logging.info("Running with no user interface.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("File Processing Engine interrupted...")

