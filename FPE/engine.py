"""FPE engine.
"""
import time
from typing import Any

from core.config import Config
from core.arguments import Arguments
from core.factory import Factory
from core.watcher import Watcher
from core.plugin import PluginLoader
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler


def load_config() -> dict[str, Any]:
    """ Load configuration.
    """

    # Load configuration file, validate and set logging.

    config = Config(Arguments())
    config.validate()
    config.set_logging()

    # Return the running config

    return config.get_config()


def load_handlers(fpe_config: dict[str, Any]) -> None:
    """Load builtin and plugin handlers.
    """

    Factory.register("CopyFile", CopyFileHandler)
    Factory.register("SFTPCopyFile", SFTPCopyFileHandler)

    PluginLoader.load(fpe_config['plugins'])


def create_watchers(watcher_configs: list[dict]) -> list[Watcher]:
    """Create list of watchers.
    """

    watcher_list: list[Watcher] = []
    for watcher_config in watcher_configs:
        current_watcher = Watcher(watcher_config)
        if current_watcher is not None:
            watcher_list.append(current_watcher)

    return watcher_list


def run_watchers(watcher_list: list[Watcher])-> None:
    """Run watchers in passed list.
    """

    try:

        for current_watcher in watcher_list:
            current_watcher.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Stop all watchers
        for current_watcher in watcher_list:
            current_watcher.stop()

    finally:
        # Wait for all watcher threads to stop
        for current_watcher in watcher_list:
            current_watcher.join()
