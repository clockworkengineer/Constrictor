"""FPE engine.
"""
import time
from typing import Any


from builtin.handler_list import fpe_handler_list
from core.constants import CONFIG_NAME, CONFIG_WATCHERS
from core.factory import Factory
from core.watcher import Watcher
from core.plugin import PluginLoader


class Engine:
    """Control class for the FPE used to create, control and delete directory watchers.
    """

    engine_config: dict[str, Any] = {}
    engine_watchers: dict[str, Watcher] = {}

    def __init__(self, engine_config: dict[str, Any]) -> None:
        """Create FPE engine.

        Args:
            engine_config (dict[str, Any]): FPE configuration.
        """
        self.engine_config = engine_config.copy()

    def create_watcher(self, watcher_config: dict[str, Any]) -> None:
        """Create a directory watcher;

        Args:
            watcher_config (dict[str, Any]): Watcher configuration.
        """
        current_watcher = Watcher(watcher_config)
        if current_watcher is not None:
            self.engine_watchers[watcher_config[CONFIG_NAME]] = current_watcher

    def delete_watcher(self, watcher_name: str) -> None:
        """Delete directory watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        self.engine_watchers[watcher_name].join()
        self.engine_watchers.pop(watcher_name)

    def start_watcher(self, watcher_name: str) -> None:
        """Start directory watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        self.engine_watchers[watcher_name].start()

    def stop_watcher(self, watcher_name: str) -> None:
        """Stop directory watcher.

        Args:
            watcher_name (str): Watcher name.
        """
        self.engine_watchers[watcher_name].stop()

    def load_handlers(self) -> None:
        """Load builtin and plugin handlers.
        """

        for handler_name in fpe_handler_list.keys():
            Factory.register(handler_name, fpe_handler_list[handler_name])

        PluginLoader.load(self.engine_config['plugins'])

    def create_watchers(self) -> None:
        """Create direcory watchers from config.
        """

        for watcher_config in self.engine_config[CONFIG_WATCHERS]:
            self.create_watcher(watcher_config)

    def run_watchers(self) -> None:
        """Run configured directory watchers.
        """

        try:

            for watcher_name in self.engine_watchers.keys():
                self.start_watcher(watcher_name)

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            # Stop all watchers
            for watcher_name in self.engine_watchers.keys():
                self.stop_watcher(watcher_name)

        finally:
            # Wait for watcher threads to end
            for watcher_name in self.engine_watchers.keys():
                self.engine_watchers[watcher_name].join()
            # Clear all watchers
            self.engine_watchers.clear()
