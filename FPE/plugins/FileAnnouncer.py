"""Simple file announcer example plugin handler.
"""

import os
import logging
from factory import Factory
import handler


class FileAnnouncer(handler.Handler):
    """
    """

    def __init__(self, handler_section):
        """Initialise handler attributes.
        """

        self.handler_name = handler_section["name"]
        self.watch_folder = handler_section["watch"]
        self.recursive = handler_section["recursive"]
        self.delete_source = handler_section["deletesource"]

    def process(self, event):
        """Print out name of any file copied into watch folder.
        """
        try:
            logging.info(
                "File %s.", event.src_path)

            if self.delete_source:
                os.remove(event.src_path)

        except ValueError as error:
            logging.error("Error in handler %s : %s",
                          self.handler_name, error)


def register() -> None:
    Factory.register("FileAnnouncer", FileAnnouncer)
