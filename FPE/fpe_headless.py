"""Run FPE headless.
"""

import logging
import time

from core.engine import Engine


def __watcher_failure_callback(self, watcher_name: str) -> None:
    """_summary_

    Args:
        watcher_name (str): _description_
    """
    if self.fpe_engine.is_watcher_running(watcher_name):
        self.fpe_engine.stop_watcher(watcher_name)


def fpe_headless(fpe_engine: Engine) -> None:
    """Run FPE without a user interface."""
    try:
        logging.info("Running with no user interface.")
        fpe_engine.set_failure_callback(__watcher_failure_callback)
        fpe_engine.startup()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("File Processing Engine interrupted...")
