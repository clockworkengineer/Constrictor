"""CopyFile builtin handler.
"""

import os
import pathlib
import shutil
import logging
from typing import Any

from core.handler import Handler
from core.error import FPEError


class CopyFileHandlerError(FPEError):
    """An error occurred in the CopyFile handler.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "CopyFileHandler Error: " + str(self.message)


class CopyFileHandler(Handler):
    """Copy file/directories.

    Copy files created in watch folder to destination folder keeping any in
    situ watch folder directory structure the same.

    Handler(Watcher) config values:
        name:           Name of handler object
        source:         Folder to watch for files
        destination:    Destination for file copy
        recursive:      Boolean == true perform recursive file watch
        deletesource:   Boolean == true delete source file on success

    """

    def __init__(self, handler_config: dict[str, Any]) -> None:
        """Copy handler config.
        """

        self.handler_config = handler_config.copy()

        self.handler_config["source"] = Handler.normalize_path(
            self.handler_config["source"])
        self.handler_config["destination"] = Handler.normalize_path(
            self.handler_config["destination"])
        
        if not os.path.exists(self.handler_config["source"] ):
            os.makedirs(self.handler_config["source"] )

        if not os.path.exists(self.handler_config["destination"] ):
            os.makedirs(self.handler_config["destination"] )


    def process(self, source_path: str) -> None:
        """Copy file from watch folder to destination.
        """
        try:

            destination_path = str(pathlib.Path(
                self.handler_config["destination"]) / source_path[len(self.handler_config["source"])+1:])

            if os.path.isfile(source_path):
                logging.info("Copying file %s to %s",
                             source_path, destination_path)
                shutil.copy2(source_path, destination_path)
                if self.handler_config["deletesource"]:
                    os.remove(source_path)

            elif os.path.isdir(source_path):
                if not os.path.exists(destination_path):
                    logging.info("Creating directory %s", source_path)
                    os.makedirs(destination_path)

        except (OSError, KeyError, ValueError) as error:
            raise CopyFileHandlerError(error) from error
