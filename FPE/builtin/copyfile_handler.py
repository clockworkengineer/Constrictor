"""FPE CopyFile builtin handler.
"""

import pathlib
import shutil
import logging

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION, CONFIG_EXITONFAILURE, \
    CONFIG_DELETESOURCE, CONFIG_RECURSIVE
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.handler import Handler
from core.error import FPEError


class CopyFileHandlerError(FPEError):
    """An error occurred in the CopyFile handler.
    """

    def __init__(self, message) -> None:
        """CopyFileHandler error.

        Args:
            message (str): Exception message.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "CopyFileHandler Error: " + self.message


class CopyFileHandler(IHandler):
    """Copy file.

    Copy files created in watch folder to destination folder.

    Handler(Watcher) config values:
        name:           Name of handler object
        source:         Folder to watch for files
        destination:    Destination for file copy
        deletesource:   Boolean == true delete source file on success
        exitonfailure:  Boolean == true exit handler on failure; generating an exception
        recursive:      Boolean == true recursively generate events in source tree 

    """

    def __init__(self, handler_config: ConfigDict) -> None:
        """Initialise copy file handler.

        Args:
            handler_config (ConfigDict): Handler configuration.

        Raises:
            CopyFileHandlerError: None passed as config.
        """

        if handler_config is None:
            raise CopyFileHandlerError("None passed as handler config.")

        self.source = handler_config[CONFIG_SOURCE]
        self.destination = handler_config[CONFIG_DESTINATION]
        self.exitonfailure = handler_config[CONFIG_EXITONFAILURE]
        self.deletesource = handler_config[CONFIG_DELETESOURCE]
        self.recursive = handler_config[CONFIG_RECURSIVE]

        Handler.setup_path(handler_config, CONFIG_SOURCE)
        Handler.setup_path(handler_config, CONFIG_DESTINATION)

    def process(self, source_path: pathlib.Path) -> bool:
        """Copy file from source(watch) directory to destination directory.

        Args:
            source_path (pathlib.Path): Source file path.

        Raises:
            CopyFileHandlerError: An error occured during file copy.
        """

        try:

            if source_path.is_file():

                destination_path: pathlib.Path = pathlib.Path(
                    self.destination) / Handler.create_relative_source(str(source_path),
                                                                       self.source)

                if not destination_path.parent.exists():
                    Handler.create_path(destination_path.parent)

                shutil.copy2(source_path, destination_path)

                logging.info("Copied file %s to %s.",
                             source_path, destination_path)

                return True

        except (OSError, KeyError, ValueError) as error:
            if self.exitonfailure:
                raise CopyFileHandlerError(error) from error
            else:
                logging.info(CopyFileHandlerError(error))

        return False
