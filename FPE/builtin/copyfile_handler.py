"""CopyFile builtin handler.
"""

import errno
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

        Handler.setup_path(self.handler_config, "source")
        Handler.setup_path(self.handler_config, "destination")

    def _copy_file(self, source_path: pathlib.Path, destination_path: pathlib.Path, delete_file :bool) -> None:
        """Copy source path to destination path retrying when an exception occurs and also
        deleting the sourec file if specified.
        """

        # File may be being copied into source so we wait until this is complete
        
        failure: bool = True
        while failure:
            try:
                with open(source_path, "rb") as source_file:
                    _ = source_file.read()
                failure = False
            except IOError as error:
                if error.errno == errno.EACCES:
                    pass
                else:
                   failure = False

        shutil.copy2(source_path, destination_path)

        logging.info("Copied file %s to %s.",
                     source_path, destination_path)
        
        if delete_file:
            source_path.unlink()

    def process(self, source_file_name: str) -> None:
        """Copy file from watch folder to destination.
        """
        try:

            with pathlib.Path(source_file_name) as source_path:

                destination_path = pathlib.Path(Handler.create_local_destination(
                    source_file_name, self.handler_config))

                if source_path.is_file():
                    self._copy_file(source_path, destination_path, self.handler_config["deletesource"])
                elif source_path.is_dir():
                    Handler.create_path(str(destination_path))

        except (OSError, KeyError, ValueError) as error:
            if self.handler_config['exitonfailure']:
                raise CopyFileHandlerError(error) from error
            else:
                logging.info(CopyFileHandlerError(error))
