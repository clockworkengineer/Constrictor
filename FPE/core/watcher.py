"""File watcher.

Use watchdog package to monitor directories and process each file created using one
of the built-in handlers or through a custom plugin handler.Note: At present the monitoring
is not recursive for easons of performance; a watcher thread can accumalate to many polling
functions for added directories.

"""

import logging
import pathlib
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.constants import CONFIG_SOURCE, CONFIG_NAME, CONFIG_TYPE, CONFIG_EXITONFAILURE, CONFIG_DELETESOURCE
from core.interface.ihandler import IHandler
from core.factory import Factory
from core.handler import Handler
from core.error import FPEError


class WatcherError(FPEError):
    """An error occurred in directory file watcher.
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

        return FPEError.error_prefix("Watcher") + str(self.message)


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


class Watcher:
    """Watch for files being copied into a folder and process.
    """

    __observer: Observer
    __running: bool

    @staticmethod
    def _display_details(handler_config) -> None:
        """Display watcher handler details and parameters.

        Args:
            handler_config (dic[str,Any]): Handler config.

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

    def __init__(self, watcher_config) -> None:
        """Initialise file watcher handler.

        Args:
            watcher_config (dict[str,Any]): Watcher config

        Raises:
            WatcherError: A watcher error has occured.
        """

        try:

            # None not a valid config

            if watcher_config is None:
                raise WatcherError("None as config passed to watcher.")

            # Default values for fields

            if CONFIG_DELETESOURCE not in watcher_config:
                watcher_config[CONFIG_DELETESOURCE] = True
            if "exitonfail" not in watcher_config:
                watcher_config[CONFIG_EXITONFAILURE] = False

            selected_handler = Factory.create(watcher_config)

            if selected_handler is not None:
                self.__observer = Observer()
                self.__observer.schedule(event_handler=WatcherHandler(
                    selected_handler), path=selected_handler.handler_config[CONFIG_SOURCE], recursive=False)
                Watcher._display_details(selected_handler.handler_config)

            else:
                self.__observer = None  # type: ignore

            self.__running = False

        except (KeyError, ValueError) as error:
            raise WatcherError(str(error)) from error

    @property
    def running(self) -> bool:
        """Is wtcher currently running ?

        Returns:
            bool: true then watcher running.
        """

        return self.__running

    def start(self) -> None:
        """Start watcher.
        """

        if self.__observer is not None:
            self.__observer.start()

        self.__running = True

    def stop(self) -> None:
        """Stop watcher.
        """

        if self.__observer is not None:
            self.__observer.stop()

        self.__running = False

    def join(self) -> None:
        """Wait for watcher thread to finish.
        """

        if self.__observer is not None:
            self.__observer.join()
