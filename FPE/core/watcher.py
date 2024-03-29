"""FPE directory/file watcher.

High level directory/file watcher control logic that uses an observer abstraction to generate
file creation events; the default abstraction using the watchdog library. 

"""

import logging
from queue import Queue


from core.observers.watchdog_observer import WatchdogObserver
from core.constants import (
    CONFIG_NAME,
    CONFIG_TYPE,
    CONFIG_EXITONFAILURE,
    CONFIG_DELETESOURCE,
    CONFIG_RECURSIVE,
)
from core.interface.ihandler import IHandler
from core.interface.iobserver import IObserver
from core.interface.iconsumer import IConsumer
from core.config import ConfigDict
from core.consumer import Consumer, FailureCallBackFunction
from core.factory import Factory
from core.error import FPEError


class WatcherError(FPEError):
    """An error occurred in directory/file watcher."""

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("Watcher") + str(self.error)


class Watcher:
    """Watch for files being copied into a folder and process."""

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
                "%s Handler [%s] running...",
                handler_config["name"],
                handler_config["type"],
            )
            for option in handler_config.keys():
                if option != CONFIG_NAME and option != CONFIG_TYPE:
                    logging.info("%s = %s", option, handler_config[option])

        except IOError as error:
            raise WatcherError(error) from error

    def __init__(
        self,
        watcher_config: ConfigDict,
        failure_callback_fn: FailureCallBackFunction = None,
    ) -> None:
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

            self.__handler: IHandler = Factory.create(watcher_config)

            self.__watcher_failure_callback: FailureCallBackFunction = (
                failure_callback_fn
            )
            if self.__handler is not None:
                self.__file_queue: Queue = Queue()
                self.__observer: IObserver = WatchdogObserver(
                    self.__file_queue, self.__handler
                )
                self.__consumer: IConsumer = Consumer(
                    self.__file_queue,
                    self.__handler,
                    self.__watcher_failure_callback,
                )
                Watcher._display_details(watcher_config)

            else:
                self.__observer = None  # type: ignore

            self.__running: bool = False

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
        """Start watcher."""

        if self.__running:
            return

        if self.__observer is None:
            self.__observer = WatchdogObserver(self.__file_queue, self.__handler)
            self.__consumer = Consumer(
                self.__file_queue,
                self.__handler,
                self.__watcher_failure_callback,
            )

        if self.__observer is not None:
            self.__observer.start()
            self.__consumer.start()
            self.__running = True
        else:
            raise WatcherError("Could not create observer.")

    def stop(self) -> None:
        """Stop watcher."""

        if self.__running:
            self.__observer.stop()
            self.__observer = None  # type: ignore
            self.__consumer.stop()
            self.__consumer = None  # type: ignore
            self.__running = False

    @property
    def status(self) -> str:
        """Return current watcher handler status."""
        return self.__handler.status()

    @property
    def files_processed(self) -> int:
        """Return the number of files processed.

        Returns:
            int: Number of files processed by handler.
        """
        return self.__handler.files_processed
