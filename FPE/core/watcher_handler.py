"""Watcher Handler.
"""

import logging
import pathlib
import time
from threading import Thread
from queue import Queue, Empty
from watchdog.events import FileSystemEventHandler

from core.constants import CONFIG_SOURCE, CONFIG_DELETESOURCE, CONFIG_FILES_PROCESSED
from core.interface.ihandler import IHandler
from core.handler import Handler


class WatcherHandler(FileSystemEventHandler):
    """Watcher handler adapter for watchdog.
    """

    __watcher_handler: IHandler
    __root_path: pathlib.Path
    __deletesource: bool
    __handler_queue: Queue
    __handler_thread: Thread

    def __init__(self, watcher_handler: IHandler) -> None:
        """Initialise watcher handler adapter.

        Args:
            watcher_handler (IHandler): Watchdog handler.
        """

        super().__init__()

        self.__watcher_handler = watcher_handler

        self.__root_path = pathlib.Path(
            self.__watcher_handler.handler_config[CONFIG_SOURCE])
        self.__deletesource = self.__watcher_handler.handler_config[CONFIG_DELETESOURCE]

        self.__watcher_handler.handler_config[CONFIG_FILES_PROCESSED] = 0

        self.__handler_queue = Queue()
        self.__handler_thread = Thread(target=self.__process)
        self.__handler_thread.daemon = True
        self.__handler_thread.start()

    def __del__(self):
        self.__handler_thread.join()

    def __process(self):

        while True:
            time.sleep(0.1)
            try:
                event = self.__handler_queue.get()
            except Empty:
                pass
            else:
                logging.debug("on_created %s.", event.src_path)
                source_path = pathlib.Path(event.src_path)  # type: ignore
                if source_path.exists():
                    Handler.wait_for_copy_completion(source_path)
                    if self.__watcher_handler.process(source_path):
                        self.__watcher_handler.handler_config[CONFIG_FILES_PROCESSED] += 1
                        if self.__deletesource:
                            Handler.remove_source(
                                self.__root_path, source_path)

    def on_created(self, event) -> None:
        """On file created event.

        Args:
            event (Any): Watchdog file created event.
        """

        self.__handler_queue.put(event)

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
