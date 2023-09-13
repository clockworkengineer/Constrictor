"""Simple file announcer example plugin handler.
"""

import pathlib
import logging

from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.factory import Factory
from core.handler import Handler
from core.error import FPEError


class FileAnnouncerHandlerError(FPEError):
    """An error occurred in the File Announcer handler."""

    def __str__(self) -> str:
        return "CopyFileHandler Error: " + str(self.message)


class FileAnnouncerHandler(IHandler):
    """File Announcer"""

    def __init__(self, handler_config: ConfigDict) -> None:
        """Copy handler config and setup source directory."""

        Handler.set_mandatory_config(self, handler_config)

    def process(self, source_path: pathlib.Path) -> bool:
        """Print out name of any file copied into watch folder."""

        try:
            logging.info("File %s.", source_path)

        except OSError as error:
            logging.info(FileAnnouncerHandlerError(error))
            self.errors += 1
            return False

        return True

    def status(self) -> str:
        """Return current handler status string

        Returns:
            str: Handler status string.
        """

        return Handler.status(self)


def register() -> None:
    """Register plugin as a watcher handler."""
    Factory.register("FileAnnouncer", FileAnnouncerHandler)
