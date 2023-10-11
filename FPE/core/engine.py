"""FPE controller engine.
"""

import logging
import json

from builtin.handler_list import fpe_handler_list
from core.constants import CONFIG_NAME, CONFIG_WATCHERS, CONFIG_FILENAME, CONFIG_NOGUI
from core.error import FPEError
from core.consumer import FailureCallBackFunction
from core.config import ConfigDict
from core.factory import Factory
from core.watcher import Watcher
from core.plugin import PluginLoader


class EngineError(FPEError):
    """An error occurred in Engine file processing."""

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("Engine") + str(self.error)


class Engine:
    """Control class for the FPE used to create, control and delete directory/file watchers."""

    __engine_config: ConfigDict = {}
    __engine_watchers: dict[str, Watcher] = {}
    __engine_watcher_failure_callback: FailureCallBackFunction =  None
    __engine_running: bool = False

    def __init__(self, engine_config: ConfigDict) -> None:
        """Create FPE engine.

        Args:
            engine_config (ConfigDict): FPE configuration.
        """

        if engine_config is None:
            raise EngineError("Engine config cannot be None.")

        # Make a copy of config for engine

        self.__engine_config = engine_config.copy()

        # Load builtin and plugin handlers.

        for handler_name, handler in fpe_handler_list.items():
            Factory.register(handler_name, handler)

        PluginLoader.load(self.__engine_config["plugins"])

    def create_watcher(self, watcher_config: ConfigDict) -> None:
        """Create a directory/file watcher.

        Args:
            watcher_config (ConfigDict): Watcher configuration.
        """
        current_watcher = Watcher(
            watcher_config, self.__engine_watcher_failure_callback
        )
        if current_watcher is not None:
            self.__engine_watchers[watcher_config[CONFIG_NAME]] = current_watcher

    def delete_watcher(self, watcher_name: str) -> None:
        """Delete directory/file watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        
        try:
            self.__engine_watchers[watcher_name].stop()
            self.__engine_watchers.pop(watcher_name)

            for watcher_config in self.__engine_config[CONFIG_WATCHERS]:
                if watcher_config[CONFIG_NAME] == watcher_name:
                    self.__engine_config[CONFIG_WATCHERS].remove(watcher_config)
                    break
        except KeyError:
            raise EngineError("Watcher name could not be found.")

    def start_watcher(self, watcher_name: str) -> None:
        """Start directory/file watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        try:
            self.__engine_watchers[watcher_name].start()
        except KeyError:
            raise EngineError("Watcher name could not be found.")

    def stop_watcher(self, watcher_name: str) -> None:
        """Stop directory/file watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        try:
            self.__engine_watchers[watcher_name].stop()
        except KeyError:
            raise EngineError("Watcher name could not be found.")

    def is_watcher_running(self, watcher_name: str) -> bool:
        """Is a named watcher running ?

        Args:
            watcher_name (str):  Watcher name.

        Returns:
            bool: true if watcher currently running
        """
        try:
            return self.__engine_watchers[watcher_name].is_running
        except KeyError:
            raise EngineError("Watcher name could not be found.")
        
    def startup(self) -> None:
        """Create directory/file watchers from config and startup."""

        for watcher_config in self.__engine_config[CONFIG_WATCHERS]:
            self.create_watcher(watcher_config)

        for watcher_name, _ in self.__engine_watchers.items():
            self.start_watcher(watcher_name)

        self.__engine_running = True

        logging.info("File Processing Engine started.")

    def shutdown(self) -> None:
        """Shutdown watchers created by engine."""
        for watcher_name, watcher in self.__engine_watchers.items():
            self.stop_watcher(watcher_name)
            watcher.stop()

        self.__engine_watchers.clear()
        self.__engine_running = False

    @property
    def is_running(self) -> bool:
        """Return true if engine running."""
        return self.__engine_running

    def running_watchers_list(self) -> list[str]:
        """Return list of current watcher names."""
        return list(self.__engine_watchers.keys())

    def running_config(self) -> ConfigDict:
        """Return engine configuration."""
        return self.__engine_config

    def return_watcher(self, watcher_name: str) -> Watcher:
        """Is a named watcher running ?

        Args:
            watcher_name (str):  Watcher name.

        Returns:
            bool: true if watcher currently running
        """

        try:
            return self.__engine_watchers[watcher_name]
        except KeyError:
            raise EngineError("Watcher name could not be found.")

    def save_config(self) -> None:
        """Save current configuration away to JSON file."""
        # Copy engine config
        config_to_save: ConfigDict = self.__engine_config.copy()
        # Remove unneeded keys
        config_to_save.pop(CONFIG_FILENAME)
        config_to_save.pop(CONFIG_NOGUI)
        # Write JSON configuration
        with open(
            self.__engine_config[CONFIG_FILENAME], "w", encoding="utf-8"
        ) as json_file:
            json_file.write(json.dumps(config_to_save, indent=1))

    def set_failure_callback(
        self, failure_callback_fn: FailureCallBackFunction
    ) -> None:
        """Set handler failure callback function.

        Args:
            failure_callback_fn (FailureCallBackFunction): Handler failure callback function.
        """
        self.__engine_watcher_failure_callback = failure_callback_fn
