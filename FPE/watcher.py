""" File watcher class.
"""

import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import factory
import handler


class WatcherHandler(FileSystemEventHandler):
    """Watcher handler adepter for watchdog.
    """

    def __init__(self, watcher_handler: handler.Handler) -> None:
        super().__init__()
        self.watcher_handler = watcher_handler

    def on_created(self, event):
        self.watcher_handler.process(event)


class Watcher:

    __observer__: Observer = None

    @staticmethod
    def __display_details__(handler_section) -> None:
        """Display watcher handler details and parameters.
        """

        try:

            logging.info("*" * 80)
            logging.info(
                "{name} Handler [{type}] running...".format(**handler_section))
            for option in handler_section.keys():
                if option != "name" and option != "type":
                    logging.info("%s = %s", option, handler_section[option])

        except Exception as e:
            logging.error(e)

    def __init__(self, watcher_config) -> None:
        try:

            # Default values for optional fields

            if not "recursive" in watcher_config:
                watcher_config["recursive"] = False
            if not "deletesource" in watcher_config:
                watcher_config["deletesource"] = True

            selected_handler = factory.create(watcher_config)

            if selected_handler is not None:
                self.__observer__ = Observer()
                self.__observer__.schedule(WatcherHandler(selected_handler), selected_handler.watch_folder,
                                           recursive=selected_handler.recursive)

                Watcher.__display_details__(watcher_config)

            else:
                self.__observer__ = None

        except Exception as e:
            logging.error(e)

    def start(self):
        if self.__observer__ is not None:
            self.__observer__.start()

    def stop(self):
        if self.__observer__ is not None:
            self.__observer__.stop()

    def join(self):
        if self.__observer__ is not None:
            self.__observer__.join()
