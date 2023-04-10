#!/usr/bin/env python3

"""File Processing Engine.

This is a generic file processing engine that sets up a watch folder and waits
for files/directories to be copied to it. Any added directories are also watched
(if recursive is set) and any added files are be processed using one of its built
in file handler classes.

Current built in file handler types:
1) Copy files/directory
2) Import CSV file to MySQL database table (missing for moment).
3) Import CSV file to SQLite database table (missing for moment).
4) SFTP copy files/directory to an SSH server (missing for moment).

usage: fpe.py [-h] file

Process files copied into watch folder using a custom handler.

positional arguments:
  file                  Configuration file

optional arguments:
  -h, --help            show this help message and exit
"""

import time
import logging
from typing import Any

from core.config import Config
from core.arguments import Arguments
from core.factory import Factory
from core.watcher import Watcher
from core.plugin import PluginLoader
from core.error import FPEError
from builtin.copyfile_handler import CopyFileHandler


__author__ = "Rob Tizzard"
__copyright__ = "Copyright 2023"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def load_config() -> dict[str, Any]:
    """ Load configuation.
    """

    # Load configuration file, validate and set logging.

    config = Config(Arguments())
    config.validate()
    config.set_logging()

    # Return the running config

    return config.get_config()


def load_handlers(fpe_config: dict[str, Any]) -> None:
    """Load builtin and plugin handers.
    """

    Factory.register("CopyFile", CopyFileHandler)

    PluginLoader.load(fpe_config['plugins'])


def create_watchers(watcher_configs: list[dict]) -> list[Watcher]:
    """Create list of watchers.
    """

    watcher_list: list[Watcher] = []
    for watcher_config in watcher_configs:
        current_watcher = Watcher(watcher_config)
        if current_watcher is not None:
            watcher_list.append(current_watcher)

    return watcher_list


def run_watchers(watcher_list: list[Watcher]):
    """Run watchers in passed list.
    """

    try:

        for current_watcher in watcher_list:
            current_watcher.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Stop all watchers
        for current_watcher in watcher_list:
            current_watcher.stop()

    finally:
        # Wait for all observer threads to stop
        for current_watcher in watcher_list:
            current_watcher.join()

########################
# FPE Main Entry Point #
########################


def fpe() -> None:
    """Main program entry point
    """

    try:

        fpe_config = load_config()

        load_handlers(fpe_config)

        watcher_list = create_watchers(fpe_config["watchers"])

        logging.info("File Processing Engine Started.")

        if watcher_list:
            run_watchers(watcher_list)
        else:
            logging.error("Error: No file handlers configured.")

        logging.info("File Processing Engine Stopped.")

    except FPEError as error:
        logging.error(error)


if __name__ == "__main__":
    fpe()
