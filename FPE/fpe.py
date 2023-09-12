#!/usr/bin/env python3

"""File Processing Engine.

This is a generic file processing engine that sets up a watch folder and waits
for files to be copied to it which are to be processed using one of its built
in file handler classes.

Current built in file handler types:
1) Copy files/directory.
2) FTP copy files/directory to an FTP server.
3) Import CSV file to MySQL database table (missing for moment).
4) Import CSV file to SQLite database table (missing for moment).

usage: fpe.py [-h] [--nogui] file

Process files copied into watch folder with a custom handler(s).

positional arguments:
  file        JSON Configuration file

options:
  -h, --help  show this help message and exit
  --nogui     run FPE with no user interface
"""

import logging

from core.error import FPEError
from core.config import Config
from core.arguments import Arguments
from core.engine import Engine
from core.constants import CONFIG_NOGUI

from fpe_headless import fpe_headless
from fpe_windowed import fpe_windowed


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
    """Main program entry point."""

    try:
        # Load configuration file, validate and set logging.

        fpe_config: Config = Config(Arguments())
        fpe_config.validate()
        fpe_config.set_logging()

        #  Create engine

        fpe_engine: Engine = Engine(fpe_config.get_config())

        logging.info("File Processing Engine Starting ...")

        # Run with selected user interface

        if fpe_config.get_config()[CONFIG_NOGUI]:
            fpe_headless(fpe_engine)
        else:
            fpe_windowed(fpe_engine)

        fpe_engine.shutdown()

    except FPEError as error:
        logging.error(error)

    finally:
        logging.info("File Processing Engine Stopped.")


if __name__ == "__main__":
    fpe()
