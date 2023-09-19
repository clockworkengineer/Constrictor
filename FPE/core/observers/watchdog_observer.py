"""FPE directory/file watcher observer.

Use watchdog package to monitor directories and process each file created using one
of the built-in handlers or through a custom plugin handler.Note: At present the monitoring
is not recursive for reasons of performance; a watcher thread can accumalate to many polling
calls for added directories.

"""

import logging

from queue import Queue
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.interface.ihandler import IHandler
from core.interface.iobserver import IObserver
from core.error import FPEError


class WatchdogObserverError(FPEError):
    """An error occurred in directory/file watcher."""

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("WatchdogObserver") + str(self.error)


class WatchdogObserver(FileSystemEventHandler, IObserver):
    """Watcher handler adapter for watchdog."""

    __file_queue: Queue
    __watchdog_observer: Observer

    def __init__(self, event_queue: Queue, watcher_handler: IHandler) -> None:
        """Initialise watcher handler adapter.

        Args:
            watcher_handler (IHandler): Watcher handler.
        """

        super().__init__()

        self.__watcher_handler = watcher_handler

        self.__file_queue = event_queue

        self.__watchdog_observer = Observer()
        self.__watchdog_observer.schedule(
            event_handler=self,
            path=self.__watcher_handler.source,
            recursive=self.__watcher_handler.recursive,
        )

    def on_created(self, event) -> None:
        """On file created event.

        Args:
            event (Any): Watchdog file created event.
        """

        logging.debug("on_created %s.", event.src_path)
        self.__file_queue.put(event)

    def start(self) -> None:
        """Start watchdog observer watching."""
        self.__watchdog_observer.start()

    def stop(self) -> None:
        """Stop watchdog observer from watching."""
        self.__watchdog_observer.stop()
        self.__watchdog_observer.join()
