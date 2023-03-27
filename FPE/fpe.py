#!/usr/bin/env python3

"""File Processing Engine.

This is a generic file processing engine that sets up a watch folder and waits 
for files/directories to be copied to it. Any added directories are also watched 
(if recursive is set) and any added files are be processed using one of its built 
in file handler classes.

Current built in file handler types:
1) Copy files/directory
2) Import CSV file to MySQL database table.
3) Import CSV file to SQLite database table.
4) SFTP copy files/directory to an SSH server.

usage: fpe.py [-h] file

Process files copied into watch folder using a custom handler.

positional arguments:
  file                  Configuration file

optional arguments:
  -h, --help            show this help message and exit
"""

import time
import logging
from config import Config, ConfigError
from arguments import Arguments, ArgumentsError
from factory import Factory, FactoryError
import watcher
import handler
import loader

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

        # Read out config dictionary to use

        config = config.config

        logging.info("File Processing Engine Started.")

        # Register built-in handlers

        Factory.register("CopyFile", handler.CopyFile)
        Factory.register("CSVFileToMySQL", handler.CSVFileToMySQL)
        Factory.register("CSVFileToSQLite", handler.CSVFileToSQLite)
        Factory.register("SFTPCopyFile", handler.SFTPCopyFile)

        # Load plug-ion handlers
        
        loader.load_plugins(config['plugins'])

        # Loop through watchers array creating file watchers for each
        
        watcher_list = []
        for watcher_config in config["watchers"]:
            current_watcher = watcher.Watcher(watcher_config)
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
            logging.error("Error: No file builtin_handlers configured.")

        logging.info("File Processing Engine Stopped.")

    except (ArgumentsError, ConfigError, FactoryError) as error:
        logging.error("FPE Error: %s.", error)


if __name__ == "__main__":
    fpe()
