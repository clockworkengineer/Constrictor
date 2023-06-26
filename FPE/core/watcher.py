"""FPE directory/file watcher.

Use watchdog package to monitor directories and process each file created using one
of the built-in handlers or through a custom plugin handler.Note: At present the monitoring
is not recursive for reasons of performance; a watcher thread can accumalate to many polling
calls for added directories.

"""

import logging
import pathlib
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.constants import CONFIG_SOURCE, CONFIG_NAME, CONFIG_TYPE, CONFIG_EXITONFAILURE, CONFIG_DELETESOURCE, CONFIG_RECURSIVE, CONFIG_FILES_PROCESSED
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

        self.__message = message

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("Watcher") + self.__message


class WatcherHandler(FileSystemEventHandler):
    """Watcher handler adapter for watchdog.
    """

    __watcher_handler: IHandler
    __existing_files: set[str]
    __root_path: pathlib.Path
    __deletesource: bool

    def __init__(self, watcher_handler: IHandler) -> None:
        """Initialise watcher handler adapter.

        Args:
            watcher_handler (IHandler): Watchdog handler.
        """

        super().__init__()

        self.__watcher_handler = watcher_handler
        self.__existing_files: set[str] = set()
        self.__root_path = pathlib.Path(
            self.__watcher_handler.handler_config[CONFIG_SOURCE])
        self.__deletesource = self.__watcher_handler.handler_config[CONFIG_DELETESOURCE]

        self.__watcher_handler.handler_config[CONFIG_FILES_PROCESSED] = 0

    def on_created(self, event) -> None:
        """On file created event.

        Args:
            event (Any): Watchdog file created event.
        """

        if event.src_path not in self.__existing_files:
            logging.debug("on_created %s.", event.src_path)
            source_path = pathlib.Path(event.src_path)  # type: ignore
            if source_path.exists():
                Handler.wait_for_copy_completion(source_path)
                if self.__watcher_handler.process(source_path):
                    if source_path.is_file():
                        self.__watcher_handler.handler_config[CONFIG_FILES_PROCESSED] += 1
                    if self.__deletesource and source_path.is_file():
                        Handler.remove_source(self.__root_path, source_path)
                    self.__existing_files.add(event.src_path)


    def on_moved(self, event):
        """On file moved event.

        Args:
            event (Any): Watchdog file moved event.

        """
        logging.debug("on_moved %s.", event.src_path)

    def on_deleted(self, event):
        """On file deleted evenet.

        Args:
            event (Any): Watchdog file deleted event.
        """
        logging.debug("on_deleted %s.", event.src_path)
        self.__existing_files.remove(event.src_path)

    def on_modified(self, event):
        """On file modified event.

        Args:
            event (Any): Watchdog file modified event.
        """
        logging.debug("on_modified %s.", event.src_path)

    def on_closed(self, event):
        """On file opened event.

        Args:
            event (Any): Watchdog file closed event.
        """
        logging.debug("on_closed %s.", event.src_path)

    def on_opened(self, event):
        """On file opened event.

        Args:
            event (Any): Watchdog file opened event.s
        """
        logging.debug("on_opened %s.", event.src_path)


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

    @property
    def files_processed(self) -> int:
        if CONFIG_FILES_PROCESSED in self.__handler.handler_config:
            return self.__handler.handler_config[CONFIG_FILES_PROCESSED]
        else:
            return 0
