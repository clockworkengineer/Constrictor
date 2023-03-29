""" Config class.

Create a configuration object from a JSON configuration file. Performing
validation on the file and generating any required exceptions as necessary

"""

import json
import logging


class ConfigError(Exception):
    """Configuration error.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "Config Error: " + str(self.message)


class Config:
    """Config class
    """

    def __init__(self, arguments) -> None:
        """Load JSON configuration file to be processed. 
        """

        try:
            with open(arguments.file, "r", encoding="utf-8") as json_file:
                self.config = json.load(json_file)
        except json.JSONDecodeError as error:
            raise ConfigError(error) from error

    def validate(self) -> None:
        """Validate config file.
        """

        # Must contain 'plugins' and 'watchers' key entries

        if "plugins" not in self.config:
            raise ConfigError("Missing config 'plugins' key")
        if "watchers" not in self.config:
            raise ConfigError("Missing config 'wa'tchers' key")

        # Each watcher entry must have a 'name' and 'type'

        for watcher_config in self.config["watchers"]:
            if "name" not in watcher_config:
                raise ConfigError("Missing config handler 'name' key")
            if "type" not in watcher_config:
                raise ConfigError("Missing config watchers 'type' key")

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

    def get_config(self) -> dict[str, str]:
        """Return config dictionary.
        """
        return self.config
