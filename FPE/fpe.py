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
from core.config import Config
from core.arguments import Arguments
from engine import Engine


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
    """Main program entry point.
    """
  
    try:

        # Load configuration file, validate and set logging.

        fpe_config: Config = Config(Arguments())
        
        fpe_config.validate()
        fpe_config.set_logging()

        #  Create engine, load handlers and create watchers

        fpe_engine: Engine = Engine(fpe_config.get_config())

        fpe_engine.load_handlers()
        fpe_engine.create_watchers()

        logging.info("File Processing Engine Started.")

        fpe_engine.run_watchers()

    except FPEError as error:
        logging.error(error)
        
    finally:
        logging.info("File Processing Engine Stopped.")

      


if __name__ == "__main__":
    fpe()
