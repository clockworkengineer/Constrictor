#!/usr/bin/env python3

"""File Processing Engine.

This is a generic file processing engine that sets up a watch folder and waits
for files to be copied to it which are to be processed using one of its built
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

import logging
from typing import Any

from core.error import FPEError
from core.watcher import Watcher
from engine import load_config, load_handlers, create_watchers, run_watchers


__author__ = "Rob Tizzard"
__copyright__ = "Copyright 2023"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


########################
# FPE Main Entry Point #
########################


def fpe() -> None:
    """Main program entry point
    """

    try:

        fpe_config: dict[str, Any] = load_config()

        load_handlers(fpe_config)

        watcher_list : list[Watcher] = create_watchers(fpe_config["watchers"])

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
