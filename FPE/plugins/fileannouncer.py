"""Simple file announcer example plugin handler.
"""

import os
import logging
from core.factory import Factory
from core.handler import Handler


class FileAnnouncerHandler(Handler):
    """File Announcer
    """

    def __init__(self, handler_config: dict[str, any]) -> None:
        """Initialise handler attributes.
        """
        self.handler_config = handler_config.copy()

    def process(self, event) -> None:
        """Print out name of any file copied into watch folder.
        """
        try:
            logging.info(
                "File %s.", event.src_path)

            if self.handler_config["deletesource"] and not os.path.isdir(event.src_path):
                os.remove(event.src_path)

        except OSError as error:
            logging.error("Error in handler %s : %s",
                          self.handler_config["name"], error)


def register() -> None:
    """Register plugin as a watcher handler.
    """
    Factory.register("FileAnnouncer", FileAnnouncerHandler)
