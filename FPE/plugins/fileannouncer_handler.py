"""Simple file announcer example plugin handler.
"""

import os
import logging
from typing import Any

from core.factory import Factory
from core.handler import Handler


class FileAnnouncerHandler(Handler):
    """File Announcer
    """

    def __init__(self, handler_config: dict[str, Any]) -> None:
        """Copy handler config.
        """
        self.handler_config = handler_config.copy()

        Handler.normalize_path(self.handler_config["source"])
        Handler.create_path(self.handler_config["source"])

    def process(self, source_path: str) -> None:
        """Print out name of any file copied into watch folder.
        """
        try:
            logging.info("File %s.", source_path)

            if self.handler_config["deletesource"] and not os.path.isdir(source_path):
                os.remove(source_path)

        except OSError as error:
            logging.error("Error in handler %s : %s",
                          self.handler_config["name"], error)


def register() -> None:
    """Register plugin as a watcher handler.
    """
    Factory.register("FileAnnouncer", FileAnnouncerHandler)
