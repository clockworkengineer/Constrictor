"""FPE consumer event processing thread.
"""

from typing import Callable
import pathlib
import time
from threading import Thread
from queue import Queue, Empty

from core.handler import Handler
from core.interface.ihandler import IHandler
from core.interface.iconsumer import IConsumer
from core.error import FPEError


class ConsumerError(FPEError):
    """An error occurred in directory/file watcher."""

    def __str__(self) -> str:
        """Return string for exception.

        Returns:
            str: Exception string.
        """

        return FPEError.error_prefix("Consumer") + str(self.error)


class Consumer(IConsumer):
    """_summary_

    Args:
        IConsumer (_type_): _description_

    Returns:
        _type_: _description_
    """

    __watcher_handler: IHandler
    __root_path: pathlib.Path
    __file_queue: Queue
    __handle_events_thread: Thread
    __engine_watcher_failure_callback: Callable[..., None] = None

    def __init__(
        self,
        event_queue: Queue,
        watcher_handler: IHandler,
        failure_callback_fn: Callable[..., None] = None,
    ) -> None:
        """Initialise consumer event processing thread.

        Args:
            watcher_handler (IHandler): Watcher handler.
        """

        self.__engine_watcher_failure_callback = failure_callback_fn
        self.__watcher_handler = watcher_handler
        self.__root_path = pathlib.Path(self.__watcher_handler.source)
        self.__file_queue = event_queue

    def __handle_event(self, source_path: pathlib.Path) -> bool:
        """Handle file event.

        Args:
            source_path (pathlib.Path): Source path to file.

        Returns:
            bool: Return true if processed successfully.
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

    def __process_event_queue(self) -> None:
        """Read event queue and process each file recieved."""
        handle_events: bool = True
        while handle_events:
            time.sleep(0.1)
            try:
                event = self.__file_queue.get()
            except Empty:
                pass
            else:
                handle_events = self.__handle_event(pathlib.Path(event.src_path))

    def start(self) -> None:
        """_summary_"""
        self.__handle_events_thread = Thread(
            target=self.__process_event_queue, name=self.__watcher_handler.name
        )
        self.__handle_events_thread.daemon = True
        self.__handle_events_thread.start()

    def stop(self) -> None:
        """_summary_"""
        self.__handle_events_thread = None
