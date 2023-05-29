"""FPE controller engine.
"""

import json

from builtin.handler_list import fpe_handler_list
from core.constants import CONFIG_NAME, CONFIG_WATCHERS, CONFIG_FILENAME, CONFIG_NOGUI
from core.config import ConfigDict
from core.factory import Factory
from core.watcher import Watcher
from core.plugin import PluginLoader


class Engine:
    """Control class for the FPE used to create, control and delete directory watchers.
    """

    __engine_config: ConfigDict = {}
    __engine_watchers: dict[str, Watcher] = {}

    def __init__(self, engine_config: ConfigDict) -> None:
        """Create FPE engine.

        Args:
            engine_config (ConfigDict): FPE configuration.
        """

        # Make a copy of config for engine

        self.__engine_config = engine_config.copy()

        # Load builtin and plugin handlers.

        for handler_name in fpe_handler_list.keys():
            Factory.register(handler_name, fpe_handler_list[handler_name])

        PluginLoader.load(self.__engine_config['plugins'])

    def create_watcher(self, watcher_config: ConfigDict) -> None:
        """Create a directory watcher.

        Args:
            watcher_config (ConfigDict): Watcher configuration.
        """
        current_watcher = Watcher(watcher_config)
        if current_watcher is not None:
            self.__engine_watchers[watcher_config[CONFIG_NAME]
                                   ] = current_watcher

    def delete_watcher(self, watcher_name: str) -> None:
        """Delete directory watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        self.__engine_watchers[watcher_name].stop()
        self.__engine_watchers.pop(watcher_name)

        for watcher_config in self.__engine_config[CONFIG_WATCHERS]:
            if watcher_config[CONFIG_NAME] == watcher_name:
                self.__engine_config[CONFIG_WATCHERS].remove(watcher_config)
                break

    def start_watcher(self, watcher_name: str) -> None:
        """Start directory watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        self.__engine_watchers[watcher_name].start()

    def stop_watcher(self, watcher_name: str) -> None:
        """Stop directory watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        self.__engine_watchers[watcher_name].stop()

    def is_watcher_running(self, watcher_name: str) -> bool:
        """Is a named watcher running ?

        Args:
            watcher_name (str):  Watcher name.

        Returns:
            bool: true if watcher currently running
        """

        return self.__engine_watchers[watcher_name].is_running

    def startup(self) -> None:
        """Create directory watchers from config and startup.
        """

        for watcher_config in self.__engine_config[CONFIG_WATCHERS]:
            self.create_watcher(watcher_config)

        for watcher_name in self.__engine_watchers.keys():
            self.start_watcher(watcher_name)

    def shutdown(self) -> None:
        """Shutdown watchers created by engine.
        """
        for watcher_name in self.__engine_watchers.keys():
            self.stop_watcher(watcher_name)
            self.__engine_watchers[watcher_name].stop()

        self.__engine_watchers.clear()

    def running_watchers_list(self) -> list[str]:
        """Return list of current watcher names.
        """
        return list(self.__engine_watchers.keys())

    def running_config(self) -> ConfigDict:
        """Return engine configuration.
        """
        return self.__engine_config

    def save_config(self) -> None:
        """Save current configuration away to JSON file.
        """
        # Copy engine config
        config_to_save: ConfigDict = self.__engine_config.copy()
        # Remove uneeded kays
        config_to_save.pop(CONFIG_FILENAME)
        config_to_save.pop(CONFIG_NOGUI)
        # Write JSON configuration
        with open(self.__engine_config[CONFIG_FILENAME], "w", encoding="utf-8") as json_file:
            json_file.write(json.dumps(config_to_save, indent=1))
