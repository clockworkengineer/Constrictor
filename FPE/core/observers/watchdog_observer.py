"""FPE directory/file watcher observer.

Use watchdog package to monitor directories and process each file created using one
of the built-in handlers or through a custom plugin handler.Note: At present the monitoring
is not recursive for reasons of performance; a watcher thread can accumalate to many polling
calls for added directories.

"""

import logging
import pathlib
import time
from threading import Thread
from queue import Queue, Empty
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.interface.ihandler import IHandler
from core.interface.iobserver import IObserver
from core.handler import Handler
from core.error import FPEError


class WatchdogObserverError(FPEError):
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

        return FPEError.error_prefix("WatchdogObserver") + self.__message


class WatchdogObserver(FileSystemEventHandler, IObserver):
    """Watcher handler adapter for watchdog.
    """

    __watcher_handler: IHandler
    __root_path: pathlib.Path
    __queue: Queue
    __thread: Thread
    __observer: Observer

    def __init__(self, watcher_handler: IHandler) -> None:
        """Initialise watcher handler adapter.

        Args:
            watcher_handler (IHandler): Watchdog handler.
        """

        super().__init__()

        self.__watcher_handler = watcher_handler

        self.__root_path = pathlib.Path(
            self.__watcher_handler.source)

        self.__queue = Queue()
        self.__thread = Thread(target=self.__process)
        self.__thread.daemon = True
        self.__thread.start()

        self.__observer = Observer()
        self.__observer.schedule(
            event_handler=self, path=self.__watcher_handler.source, recursive=self.__watcher_handler.recursive)

    def __process(self):

        while True:
            time.sleep(0.1)
            try:
                event = self.__queue.get()
            except Empty:
                pass
            else:
                logging.debug("on_created %s.", event.src_path)
                source_path = pathlib.Path(event.src_path)  # type: ignore
                if source_path.exists():
                    Handler.wait_for_copy_completion(source_path)
                    if self.__watcher_handler.process(source_path):
                        self.__watcher_handler.files_processed += 1
                        if self.__watcher_handler.deletesource:
                            Handler.remove_source(
                                self.__root_path, source_path)

    def on_created(self, event) -> None:
        """On file created event.

        Args:
            event (Any): Watchdog file created event.
        """

        self.__queue.put(event)

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

    def start(self) -> None:
        """Start watchdog observer watching.
        """
        self.__observer.start()

    def stop(self) -> None:
        """Stop watchdog observer from watching.
        """
        self.__observer.stop()
        self.__observer.join()
