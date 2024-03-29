"""FPE Config.

Create a configuration dictionary from a JSON configuration file. Performing
validation on the JSON and generating any required exceptions as necessary.

"""

import json
import logging
from typing import Any

from core.constants import (
    CONFIG_WATCHERS,
    CONFIG_NOGUI,
    CONFIG_FILENAME,
    CONFIG_MANDATORY_KEYS,
    CONFIG_WATCHER_MANDATORY_KEYS,
)
from core.error import FPEError
from core.arguments import Arguments

ConfigDict = dict[str, Any]


class ConfigError(FPEError):
    """An error occurred whilst processing FPE configuration file."""

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """
        return FPEError.error_prefix("Config") + str(self.error)


class Config:
    """Load JSON configuration into a dictionary and validate it."""

    def __init__(self, arguments: Arguments) -> None:
        """Load JSON configuration file to be processed.

        Args:
            arguments (Arguments): Passed arguments.

        Raises:
            ConfigError: An error was found in the config.
        """

        try:
            # Load config file
            with open(arguments.file, "r", encoding="utf-8") as json_file:
                self.__config = json.load(json_file)
            # Set UI flag (JSON file setting overrides any command line option)
            if CONFIG_NOGUI not in self.__config:
                self.__config[CONFIG_NOGUI] = arguments.nogui
            # Save away config file name
            self.__config[CONFIG_FILENAME] = arguments.file
        except json.JSONDecodeError as error:
            raise ConfigError(error) from error

    def validate(self) -> None:
        """Validate config file."""

        # Must contain 'plugins' and 'watchers' key entries

        for key in CONFIG_MANDATORY_KEYS:
            if key not in self.__config:
                raise ConfigError(f"Missing config '{key}' key")

        # Each watcher entry must have a 'name', 'type' and 'source' keys

        for watcher_config in self.__config[CONFIG_WATCHERS]:
            for key in CONFIG_WATCHER_MANDATORY_KEYS:
                if key not in watcher_config:
                    raise ConfigError(f"Missing watcher '{key}' key")

    def set_logging(self) -> None:
        """Set type of logging to be used."""

        # Default logging parameters

        logging_params: dict[str, Any] = {
            "level": logging.INFO,
            "format": "%(asctime)s:%(message)s",
        }

        # Read in any logging options, merge with default

        if "logging" in self.__config:
            logging_params.update(self.__config["logging"])
            # If level passed in then convert to int.
            if logging_params["level"] is not int:
                logging_params["level"] = int(logging_params["level"])

        logging.basicConfig(**logging_params)  # Set logging options

    @property
    def config(self) -> ConfigDict:
        """Return config dictionary.

        Returns:
            ConfigDict: Config dictionary.
        """

        return self.__config
