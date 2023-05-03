"""CopyFile builtin handler.
"""

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

    Copy files created in watch folder to destination folder.

    Handler(Watcher) config values:
        name:           Name of handler object
        source:         Folder to watch for files
        destination:    Destination for file copy
        deletesource:   Boolean == true delete source file on success
        exitonfailure:  Boolean == true exit handler on failure; generating an exception

    """

    def __init__(self, handler_config: dict[str, Any]) -> None:
        """Copy handler config.
        """

        if handler_config is None:
            raise CopyFileHandlerError("None passed as handler config.")

        self.handler_config = handler_config.copy()

        Handler.setup_path(self.handler_config, "source")
        Handler.setup_path(self.handler_config, "destination")

    def _copy_file(self, source_path: pathlib.Path, destination_path: pathlib.Path, delete_source: bool) -> None:
        """Copy source path to destination path.
        """

        Handler.wait_for_copy_completion(source_path)
        source_path.chmod(source_path.stat().st_mode | 0o664)
        shutil.copy2(source_path, destination_path)

        logging.info("Copied file %s to %s.",
                     source_path, destination_path)

        if delete_source:
            source_path.unlink()

    def process(self, source_file_name: str) -> None:
        """Copy file from source(watch) directory to destination directory.
        """
        try:

            with pathlib.Path(source_file_name) as source_path:

                destination_path = Handler.create_local_destination(
                    source_path, self.handler_config)

                if source_path.is_file():
                    self._copy_file(source_path, destination_path,
                                    self.handler_config["deletesource"])
                elif source_path.is_dir():
                    Handler.create_path(str(destination_path))

        except (OSError, KeyError, ValueError) as error:
            if self.handler_config['exitonfailure']:
                raise CopyFileHandlerError(error) from error
            else:
                logging.info(CopyFileHandlerError(error))
