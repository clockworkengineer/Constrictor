"""FPE directory/file watcher.

High level directory/file watcher control logic that uses an observer abstraction to generate
file creation events; the default abstraction using the watchdog library. 

"""

import logging

from core.observers.watchdog_observer import WatchdogObserver
from core.constants import CONFIG_NAME, CONFIG_TYPE, CONFIG_EXITONFAILURE, CONFIG_DELETESOURCE, CONFIG_RECURSIVE
from core.interface.ihandler import IHandler
from core.interface.iobserver import IObserver
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
    __observer: IObserver
    __running: bool

    @staticmethod
    def _display_details(handler_config: ConfigDict) -> None:
        """Display watcher handler details and parameters.

        Args:
            handler_config (ConfigDict): Handler config.

        Raises:
            WatcherError: An error has occurred whilst running the watcher.
        """

        try:
            logging.info("*" * 80)
            logging.info(
                "%s Handler [%s] running...", handler_config['name'], handler_config['type'])
            for option in handler_config.keys():
                if option != CONFIG_NAME and option != CONFIG_TYPE:
                    logging.info("%s = %s", option, handler_config[option])

        except IOError as error:
            raise WatcherError(error) from error

    def __init__(self, watcher_config: ConfigDict) -> None:
        """Initialise directory/file watcher.

        Args:
            watcher_config (ConfigDict): Watcher config

        Raises:
            WatcherError: A watcher error has occurred.
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
                self.__observer = WatchdogObserver(self.__handler)
                Watcher._display_details(watcher_config)

            else:
                self.__observer = None  # type: ignore

            self.__running = False

        except (KeyError, ValueError) as error:
            raise WatcherError(error) from error

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

        if self.__observer is None:
            self.__observer = WatchdogObserver(self.__handler)

        if self.__observer is not None:
            self.__observer.start()
            self.__running = True
        else:
            raise WatcherError("Could not create observer.")

    def stop(self) -> None:
        """Stop watcher.
        """

        if self.__observer is not None:
            self.__observer.stop()
            self.__observer = None  # type: ignore
            self.__running = False

    @property
    def files_processed(self) -> int:
        return self.__handler.files_processed
