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

########################
# FPE Main Entry Point #
########################


def fpe() -> None:
    """Main program entry point
    """

    try:

        # Load configuration file, validate and set logging

        config = Config(Arguments())
        config.validate()
        config.set_logging()

        # Get the running config

        fpe_config = config.get_config()

        logging.info("File Processing Engine Started.")

        # Register builtin handlers

        Factory.register("CopyFile", CopyFileHandler)

        # Load plugin handlers

        PluginLoader.load(fpe_config['plugins'])

        # Loop through watchers array creating file watchers for each

        watcher_list = []
        for watcher_config in fpe_config["watchers"]:
            current_watcher = Watcher(watcher_config)
            if current_watcher is not None:
                watcher_list.append(current_watcher)

        # If list not empty observer folders

        if watcher_list:
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

        else:
            logging.error("Error: No file handlers configured.")

        logging.info("File Processing Engine Stopped.")

    except FPEError as error:
        logging.error(error)


if __name__ == "__main__":
    fpe()
