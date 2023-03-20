import os
import logging
import factory
import handler


class FileAnnouncer(handler.Handler):

    def __init__(self, handler_section):
        """ Initialise handler attributes and log details."""

        self.handler_name = handler_section["name"]
        self.watch_folder = handler_section["watch"]
        self.recursive = handler_section["recursive"]
        self.delete_source = handler_section["deletesource"]

    def process(self, event):
        """Copy file from watch folder to destination."""
        try:
            logging.info(
                "File %s.", event.src_path)

            if self.delete_source:
                os.remove(event.src_path)

        except Exception as error:
            logging.error("Error in handler %s : %s",
                          self.handler_name, error)


def register() -> None:
    factory.register("FileAnnouncer", FileAnnouncer)
