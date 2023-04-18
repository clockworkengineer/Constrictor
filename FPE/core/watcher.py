""" File watcher.
"""

import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.factory import Factory
from core.handler import Handler
from core.error import FPEError


class WatcherError(FPEError):
    """An error occurred in a file watcher.
    """

    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return "FPE Watcher Error: " + str(self.message)


class WatcherHandler(FileSystemEventHandler):
    """Watcher handler adapter for watchdog.
    """

    def __init__(self, watcher_handler: Handler) -> None:
        """Initialise watcher handler adapter.
        """
        super().__init__()
        self.watcher_handler = watcher_handler

    def on_created(self, event):
        self.watcher_handler.process(event.src_path)


class Watcher:
    """Watch for files being copied into a folder and process.
    """

    _observer: Observer

    @staticmethod
    def __display_details(handler_section) -> None:
        """Display watcher handler details and parameters.
        """
        try:
            logging.info("*" * 80)
            logging.info(
                "%s Handler [%s] running...", handler_section['name'], handler_section['type'])
            for option in handler_section.keys():
                if option != "name" and option != "type":
                    logging.info("%s = %s", option, handler_section[option])

        except IOError as error:
            raise WatcherError(error) from error

    def __init__(self, watcher_config) -> None:
        """Initialise file watcher handler.
        """
        try:

            # None not a valid config
            
            if watcher_config is None:
                raise WatcherError("None as config passed to watcher.")

            # Default values for optional fields

            if "recursive" not in watcher_config:
                watcher_config["recursive"] = False
            if "deletesource" not in watcher_config:
                watcher_config["deletesource"] = True

            selected_handler = Factory.create(watcher_config)

            if selected_handler is not None:
                self._observer = Observer()
                self._observer.schedule(event_handler=WatcherHandler(selected_handler), path=watcher_config["watch"],
                                         recursive=watcher_config["recursive"])

                Watcher.__display_details(watcher_config)

            else:
                self._observer = None  # type: ignore
                
            self._started = False

        except (KeyError, ValueError) as error:
            raise WatcherError(error) from error
        
    @property
    def started(self):
        return self._started

    def start(self) -> None:
        """Start watcher.
        """
        if self._observer is not None:
            self._observer.start()
            
        self._started = True

    def stop(self) -> None:
        """Stop watcher.
        """
        if self._observer is not None:
            self._observer.stop()
            
        self._started = False

    def join(self) -> None:
        """Wait for watcher thread to finish.
        """
        if self._observer is not None:
            self._observer.join()
            

    
