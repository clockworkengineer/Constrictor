"""FPE directory/file watcher.

Use watchdog package to monitor directories and process each file created using one
of the built-in handlers or through a custom plugin handler.Note: At present the monitoring
is not recursive for easons of performance; a watcher thread can accumalate to many polling
functions for added directories.

"""

import logging
import pathlib
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.constants import CONFIG_SOURCE, CONFIG_NAME, CONFIG_TYPE, CONFIG_EXITONFAILURE, CONFIG_DELETESOURCE, CONFIG_RECURSIVE
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.factory import Factory
from core.handler import Handler
from core.error import FPEError


class WatcherError(FPEError):
    """An error occurred in directory/file watcher.
    """

    def __init__(self, message: str) -> None:
        """Create watcher exception.

        Args:
            message (str): Exception message.
        """

        self.message = message

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("Watcher") + self.message


class WatcherHandler(FileSystemEventHandler):
    """Watcher handler adapter for watchdog.
    """

    def __init__(self, watcher_handler: IHandler) -> None:
        """Initialise watcher handler adapter.

        Args:
            watcher_handler (IHandler): Watchdog handler.
        """

        super().__init__()
        self.watcher_handler = watcher_handler

    def on_created(self, event):
        """On file created event.

        Args:
            event (Any): Watchdog event.
        """

        source_path = pathlib.Path(event.src_path)  # type: ignore
        Handler.wait_for_copy_completion(source_path)
        source_path.chmod(source_path.stat().st_mode | 0o664)
        self.watcher_handler.process(source_path)
        if self.watcher_handler.handler_config[CONFIG_DELETESOURCE] and source_path.is_file():
            source_path.unlink()


class Watcher:
    """Watch for files being copied into a folder and process.
    """

    __handler: IHandler
    __observer: Observer
    __running: bool

    @staticmethod
    def _create_observer(handler: IHandler) -> Observer:
        observer: Observer = Observer()
        observer.schedule(event_handler=WatcherHandler(
            handler), path=handler.handler_config[CONFIG_SOURCE], recursive=handler.handler_config[CONFIG_RECURSIVE])
        return observer

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
                self.__observer = Watcher._create_observer(self.__handler)
                Watcher._display_details(self.__handler.handler_config)

            else:
                self.__observer = None  # type: ignore

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

        if self.__observer is None:
            self.__observer = Watcher._create_observer(self.__handler)

        if self.__observer is not None:
            self.__observer.start()
            self.__running = True
        else:
            raise WatcherError("Could not create watchdog observer.")

    def stop(self) -> None:
        """Stop watcher.
        """

        if self.__observer is not None:
            self.__observer.stop()
            self.__observer.join()
            self.__observer = None  # type: ignore
            self.__running = False
