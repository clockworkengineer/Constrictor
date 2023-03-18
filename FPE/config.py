""" Config handling code.
"""

import sys
import json
import logging

class ConfigError(Exception):
    """Configuation error"""  

def load_config(arguments):
    """Load configuration file and set logging parameters"""

    try:

        # Read in config file

        with open(arguments.file, "r", encoding="utf-8") as json_file:
            config = json.load(json_file)

        if not "watchers" in config:
            raise ConfigError("Missing config watchers key.")

        for watcher_config in config["watchers"]:
            if not "name" in watcher_config:
                raise ConfigError("Missing config handler name key.")
            if not "type" in watcher_config:
                raise ConfigError("Missing config watchers type key.")

        # Default logging parameters

        logging_params = {"level": logging.INFO,
                          "format": "%(asctime)s:%(message)s"}

        # Read in any logging options, merge with default

        if "logging" in config:
            logging_params.update(config["logging"])
            # If level passed in then convert to int.
            if logging_params["level"] is not int:
                logging_params["level"] = int(logging_params["level"])

        logging.basicConfig(**logging_params)  # Set logging options

    except ConfigError as error:
        logging.error(error)
        sys.exit(1)

    return config
