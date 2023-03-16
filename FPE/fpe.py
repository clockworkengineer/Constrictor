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

Process files copied into watch folder with a custom handler.

positional arguments:
  file                  Configuration file

optional arguments:
  -h, --help            show this help message and exit
"""

import sys
import os
import logging
import argparse

from observer import create_observer, observe_folders
from config import load_config
from arguments import load_arguments

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
    """Main program entry point"""

    config = load_config(load_arguments())

    logging.info('File Processing Engine Started.')

    observers_list = []

    # Loop through watchers array creating file observers for each

    for handler_config in config['watchers']:

        observer = create_observer(handler_config)
        if observer is not None:
            observers_list.append(observer)

    # If list not empty observer folders

    if observers_list:
        observe_folders(observers_list)

    else:
        logging.error('Error: No file handlers configured.')

    logging.info('File Processing Engine Stopped.')


if __name__ == '__main__':
    fpe()
