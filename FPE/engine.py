"""FPE engine.
"""
import time
from typing import Any

from core.factory import Factory
from core.watcher import Watcher
from core.plugin import PluginLoader
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler


class Engine:

    engine_config: dict[str, Any] = {}
    watcher_list: list[Watcher] = []

    def __init__(self, config: dict[str, Any]) -> None:

        self.engine_config = config.copy()

    def load_handlers(self) -> None:
        """Load builtin and plugin handlers.
        """

        Factory.register("CopyFile", CopyFileHandler)
        Factory.register("SFTPCopyFile", SFTPCopyFileHandler)

        PluginLoader.load(self.engine_config['plugins'])

    def create_watchers(self) -> None:
        """Create list of watchers.
        """

        for watcher_config in self.engine_config["watchers"]:
            current_watcher = Watcher(watcher_config)
            if current_watcher is not None:
                self.watcher_list.append(current_watcher)

    def run_watchers(self) -> None:
        """Run watchers in passed list.
        """

        try:

            for current_watcher in self.watcher_list:
                current_watcher.start()

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            # Stop all watchers
            for current_watcher in self.watcher_list:
                current_watcher.stop()

        finally:
            # Wait for all watcher threads to stop
            for current_watcher in self.watcher_list:
                current_watcher.join()
