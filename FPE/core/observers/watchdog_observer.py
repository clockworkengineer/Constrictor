"""FPE directory/file watcher observer.

Use watchdog package to monitor directories and process each file created using one
of the built-in handlers or through a custom plugin handler.Note: At present the monitoring
is not recursive for reasons of performance; a watcher thread can accumalate to many polling
calls for added directories.

"""

import logging
from typing import Callable
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
    """An error occurred in directory/file watcher."""

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("WatchdogObserver") + str(self.error)


class WatchdogObserver(FileSystemEventHandler, IObserver):
    """Watcher handler adapter for watchdog."""

    __watcher_handler: IHandler
    __root_path: pathlib.Path
    __queue: Queue
    __thread: Thread
    __observer: Observer
    __engine_watcher_failure_callback: Callable[..., None] = None

    def __init__(
        self, watcher_handler: IHandler, failure_callback_fn: Callable[..., None] = None
    ) -> None:
        """Initialise watcher handler adapter.

        Args:
            watcher_handler (IHandler): Watchdog handler.
        """

        super().__init__()

        self.__engine_watcher_failure_callback = failure_callback_fn

        self.__watcher_handler = watcher_handler

        self.__root_path = pathlib.Path(self.__watcher_handler.source)

        self.__queue = Queue()
        self.__thread = Thread(
            target=self.__event_queue_thread, name=watcher_handler.name
        )
        self.__thread.daemon = True
        self.__thread.start()

        self.__observer = Observer()
        self.__observer.schedule(
            event_handler=self,
            path=self.__watcher_handler.source,
            recursive=self.__watcher_handler.recursive,
        )

    def __handle_event(self, source_path: pathlib.Path) -> bool:
        """_summary_

        Args:
            source_path (pathlib.Path): _description_

        Returns:
            bool: _description_
        """
        if source_path.exists():
            Handler.wait_for_copy_completion(source_path)
            if self.__watcher_handler.process(source_path):
                self.__watcher_handler.files_processed += 1
                if self.__watcher_handler.delete_source:
                    Handler.remove_source(self.__root_path, source_path)
            else:
                if self.__watcher_handler.exit_on_failure:
                    if self.__engine_watcher_failure_callback is not None:
                        self.__engine_watcher_failure_callback(
                            self.__watcher_handler.name
                        )
                    return False
        return True

    def __event_queue_thread(self):
        """_summary_
        """
        handle_events: bool = True
        while handle_events:
            time.sleep(0.1)
            try:
                event = self.__queue.get()
            except Empty:
                pass
            else:
                handle_events = self.__handle_event(pathlib.Path(event.src_path))

    def on_created(self, event) -> None:
        """On file created event.

        Args:
            event (Any): Watchdog file created event.
        """

        logging.debug("on_created %s.", event.src_path)
        self.__queue.put(event)

    def start(self) -> None:
        """Start watchdog observer watching."""
        self.__observer.start()

    def stop(self) -> None:
        """Stop watchdog observer from watching."""
        self.__observer.stop()
        self.__observer.join()
