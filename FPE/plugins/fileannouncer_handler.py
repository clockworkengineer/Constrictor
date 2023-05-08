"""Simple file announcer example plugin handler.
"""

import os
import pathlib
import logging
from typing import Any

from core.factory import Factory
from core.handler import IHandler, Handler


class FileAnnouncerHandler(IHandler):
    """File Announcer
    """

    def __init__(self, handler_config: dict[str, Any]) -> None:
        """Copy handler config.
        """
        self.handler_config = handler_config.copy()

        self.handler_config["source"] = Handler.normalize_path(
            self.handler_config["source"])
        Handler.create_path(pathlib.Path(self.handler_config["source"]))

    def process(self,  source_path: pathlib.Path) -> None:
        """Print out name of any file copied into watch folder.
        """
        try:
            logging.info("File %s.", source_path)

            if self.handler_config["deletesource"] and not source_path.is_dir():
                source_path.unlink()

        except OSError as error:
            logging.error("Error in handler %s : %s",
                          self.handler_config["name"], error)


def register() -> None:
    """Register plugin as a watcher handler.
    """
    Factory.register("FileAnnouncer", FileAnnouncerHandler)
