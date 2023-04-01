""" File watcher.
"""

import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from core.factory import Factory
from core.handler import Handler


class WatcherError(Exception):
    """An error occured in a file watcher.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "Watcher Error: " + str(self.message)


class WatcherHandler(FileSystemEventHandler):
    """Watcher handler adapter for watchdog.
    """

    def __init__(self, watcher_handler: Handler) -> None:
        """Initialise watcher handler adapter.
        """
        super().__init__()
        self.watcher_handler = watcher_handler

    def on_created(self, event):
        self.watcher_handler.process(event)


class Watcher:
    """Watch for files being copied into a folder and process.
    """
    __observer: Observer = None

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
            raise WatcherError from error

    def __init__(self, watcher_config) -> None:
        """Initialise file watcher handler.
        """
        try:
            # Default values for optional fields

            if "recursive" not in watcher_config:
                watcher_config["recursive"] = False
            if "deletesource" not in watcher_config:
                watcher_config["deletesource"] = True

            selected_handler = Factory.create(watcher_config)

            if selected_handler is not None:
                self.__observer = Observer()
                self.__observer.schedule(event_handler=WatcherHandler(selected_handler), path=watcher_config["watch"],
                                         recursive=watcher_config["recursive"])

                Watcher.__display_details(watcher_config)

            else:
                self.__observer = None

        except (KeyError, ValueError) as error:
            raise WatcherError from error

    def start(self) -> None:
        """Start watcher.
        """
        if self.__observer is not None:
            self.__observer.start()

    def stop(self) -> None:
        """Stop watcher.
        """
        if self.__observer is not None:
            self.__observer.stop()

    def join(self) -> None:
        """Wait for watcher thread to finish.
        """
        if self.__observer is not None:
            self.__observer.join()
