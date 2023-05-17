"""Simple file announcer example plugin handler.
"""

import pathlib
import logging

from core.constants import CONFIG_SOURCE, CONFIG_NAME
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.factory import Factory
from core.handler import Handler


class FileAnnouncerHandler(IHandler):
    """File Announcer
    """

    def __init__(self, handler_config: ConfigDict) -> None:
        """Copy handler config.
        """
        self.handler_config = handler_config.copy()
        
        Handler.setup_path(self.handler_config, CONFIG_SOURCE)

    def process(self,  source_path: pathlib.Path) -> None:
        """Print out name of any file copied into watch folder.
        """
        try:
            logging.info("File %s.", source_path)

        except OSError as error:
            logging.error("Error in handler %s : %s",
                          self.handler_config[CONFIG_NAME], error)


def register() -> None:
    """Register plugin as a watcher handler.
    """
    Factory.register("FileAnnouncer", FileAnnouncerHandler)
