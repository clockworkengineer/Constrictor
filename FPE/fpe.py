#!/usr/bin/env python3

"""File Processing Engine.

This is a generic file processing engine that sets up a watch folder and waits 
for files/directories to be copied to it. Any added directories are also watched 
(if recursive is set) but any added files are be processed using one of its built 
in file handler classes.

Current built in file handler types:
1) Copy files/directory
2) Import CSV file to MySQL database table.
3) Import CSV file to SQLite database table.
4) SFTP copy files/directory to an SSH server.

usage: fpe.py [-h] [-n NAME] file

Process files copied into watch folder with a custom handler.

positional arguments:
  file                  Configration file

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  File handler name
"""

import sys
import os
import logging
import argparse

from observer import create_observer, observe_folders
from config import load_config, get_config_section
from factory import create_event_handler


__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def load_arguments():
    """Load and parse command line arguments"""

    parser = argparse.ArgumentParser(
        description='Process files copied into watch folder with a custom handler.')
    parser.add_argument('file', help='Configration file')
    parser.add_argument('-n', '--name', help="File handler name")

    arguments = parser.parse_args()

    if not os.path.exists(arguments.file):
        print('Error: Non-existant config file passed to FPE.')
        sys.exit(1)

    return arguments


########################
# FPE Main Entry Point #
########################


def fpe():
    """Main program entry point"""

    arguments = load_arguments()

    config = load_config(arguments)

    logging.info('File Processing Engine Started.')

    observers_list = []

    # Loop through config sections creating file observers

    for handler_name in config.sections():

        observer = create_observer(config, handler_name)
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
