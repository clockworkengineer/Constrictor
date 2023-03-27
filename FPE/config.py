""" Config class.
"""

import json
import logging


class ConfigError(Exception):
    """Configuration error
    """


class Config:
    """Config class
    """

    def __init__(self, arguments) -> None:
        """Load configuration file to be processed. 
        """

        with open(arguments.file, "r", encoding="utf-8") as json_file:
            self.config = json.load(json_file)

    def validate(self) -> None:
        """Validate config file.
        """

        if "plugins" not in self.config:
            raise ConfigError("Missing config plugins key.")
        if "watchers" not in self.config:
            raise ConfigError("Missing config watchers key.")

        for watcher_config in self.config["watchers"]:
            if "name" not in watcher_config:
                raise ConfigError("Missing config handler name key.")
            if "type" not in watcher_config:
                raise ConfigError("Missing config watchers type key.")

    def set_logging(self) -> None:
        """Set type of logging to be used.
        """

        # Default logging parameters

        logging_params = {"level": logging.INFO,
                          "format": "%(asctime)s:%(message)s"}

        # Read in any logging options, merge with default

        if "logging" in self.config:
            logging_params.update(self.config["logging"])
            # If level passed in then convert to int.
            if logging_params["level"] is not int:
                logging_params["level"] = int(logging_params["level"])

        logging.basicConfig(**logging_params)  # Set logging options
