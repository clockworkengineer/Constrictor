""" File watcher class.
"""

import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from factory import Factory
import handler


class WatcherHandler(FileSystemEventHandler):
    """Watcher handler adapter for watchdog.
    """

    def __init__(self, watcher_handler: handler.Handler) -> None:
        """Initialise watcher handler adapter.
        """
        super().__init__()
        self.watcher_handler = watcher_handler

    def on_created(self, event):
        self.watcher_handler.process(event)


class Watcher:

    __observer: Observer = None

    @staticmethod
    def __display_details(handler_section) -> None:
        """Display watcher handler details and parameters.
        """

        try:

            logging.info("*" * 80)
            logging.info(
                "{name} Handler [{type}] running...".format(**handler_section))
            for option in handler_section.keys():
                if option != "name" and option != "type":
                    logging.info("%s = %s", option, handler_section[option])

        except Exception as error:
            logging.error(error)

    def __init__(self, watcher_config) -> None:
        try:

            # Default values for optional fields

            if "recursive" not in watcher_config:
                watcher_config["recursive"] = False
            if "deletesource" not in watcher_config:
                watcher_config["deletesource"] = True

            selected_handler = Factory.create(watcher_config)

            if selected_handler is not None:
                self.__observer = Observer()
                self.__observer.schedule(WatcherHandler(selected_handler), selected_handler.watch_folder,
                                         recursive=selected_handler.recursive)

                Watcher.__display_details(watcher_config)

            else:
                self.__observer = None

        except Exception as e:
            logging.error(e)

    def start(self):
        if self.__observer is not None:
            self.__observer.start()

    def stop(self):
        if self.__observer is not None:
            self.__observer.stop()

    def join(self):
        if self.__observer is not None:
            self.__observer.join()
