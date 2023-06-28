"""FPE directory/file watcher.

Use watchdog package to monitor directories and process each file created using one
of the built-in handlers or through a custom plugin handler.Note: At present the monitoring
is not recursive for reasons of performance; a watcher thread can accumalate to many polling
calls for added directories.

"""

import logging

from core.watcher_handler import WatcherHandler
from core.constants import CONFIG_NAME, CONFIG_TYPE, CONFIG_EXITONFAILURE, CONFIG_DELETESOURCE, CONFIG_RECURSIVE, CONFIG_FILES_PROCESSED
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.factory import Factory
from core.error import FPEError


class WatcherError(FPEError):
    """An error occurred in directory/file watcher.
    """

    def __init__(self, message: str) -> None:
        """Create watcher exception.

        Args:
            message (str): Exception message.
        """

        self.__message = message

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("Watcher") + self.__message


class Watcher:
    """Watch for files being copied into a folder and process.
    """

    __handler: IHandler
    __watcher_handler: WatcherHandler
    __running: bool

    @staticmethod
    def _display_details(handler_config: ConfigDict) -> None:
        """Display watcher handler details and parameters.

        Args:
            handler_config (ConfigDict): Handler config.

        Raises:
            WatcherError: An error has occured whilst running the watcher.
        """

        try:
            logging.info("*" * 80)
            logging.info(
                "%s Handler [%s] running...", handler_config['name'], handler_config['type'])
            for option in handler_config.keys():
                if option != CONFIG_NAME and option != CONFIG_TYPE:
                    logging.info("%s = %s", option, handler_config[option])

        except IOError as error:
            raise WatcherError(str(error)) from error

    def __init__(self, watcher_config: ConfigDict) -> None:
        """Initialise file watcher handler.

        Args:
            watcher_config (ConfigDict): Watcher config

        Raises:
            WatcherError: A watcher error has occured.
        """

        try:

            # None not a valid config

            if watcher_config is None:
                raise WatcherError("None as config passed to watcher.")

            # Default values for config keys

            if CONFIG_DELETESOURCE not in watcher_config:
                watcher_config[CONFIG_DELETESOURCE] = True
            if CONFIG_EXITONFAILURE not in watcher_config:
                watcher_config[CONFIG_EXITONFAILURE] = False
            if CONFIG_RECURSIVE not in watcher_config:
                watcher_config[CONFIG_RECURSIVE] = False

            self.__handler = Factory.create(watcher_config)

            if self.__handler is not None:
                self.__watcher_handler = WatcherHandler(self.__handler)
                Watcher._display_details(self.__handler.handler_config)

            else:
                self.__watcher_handler = None  # type: ignore

            self.__running = False

        except (KeyError, ValueError) as error:
            raise WatcherError(str(error)) from error

    @property
    def is_running(self) -> bool:
        """Is watcher currently running ?

        Returns:
            bool: true then watcher running.
        """

        return self.__running

    def start(self) -> None:
        """Start watcher.
        """

        if self.__running:
            return

        if self.__watcher_handler is None:
            self.__watcher_handler = WatcherHandler(self.__handler)

        if self.__watcher_handler is not None:
            self.__watcher_handler.start()
            self.__running = True
        else:
            raise WatcherError("Could not create watchdog observer.")

    def stop(self) -> None:
        """Stop watcher.
        """

        if self.__watcher_handler is not None:
            self.__watcher_handler.stop()
            self.__watcher_handler = None  # type: ignore
            self.__running = False

    @property
    def files_processed(self) -> int:
        if CONFIG_FILES_PROCESSED in self.__handler.handler_config:
            return self.__handler.handler_config[CONFIG_FILES_PROCESSED]
        else:
            return 0
