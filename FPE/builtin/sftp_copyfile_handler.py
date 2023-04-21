"""SFTPCopyFile builtin handler.
"""


import os
import pathlib
import logging
from typing import Any
import pysftp

from core.handler import Handler
from core.error import FPEError


class SFTPCopyFileHandlerError(FPEError):
    """An error occurred in the SFTPCopyFile handler.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "SFTPCopyFileHandler Error: " + str(self.message)


class SFTPCopyFileHandler(Handler):
    """SFTP Copy file/directories.

    SFTP Copy files created in watch folder to destination folder on remote SSH
    server keeping any in situ watch folder directory structure the same.

    Attributes:
        name           Name of handler object
        source         Folder to watch for files
        server         SSH Server
        user           SSH Server username
        password       SSH Server user password
        destination    Destination for copy
        recursive:     Boolean == true perform recursive file watch
        deletesource   Boolean == true delete source file on success
    """

    def __init__(self, handler_config: dict[str, Any]) -> None:
        """ Initialise handler attributes.
        """

        self.handler_config = handler_config.copy()

        self.handler_config["source"] = Handler.normalize_path(
            self.handler_config["source"])
        self.handler_config["destination"] = Handler.normalize_path(
            self.handler_config["destination"])

        Handler.create_path(self.handler_config["source"])

        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def process(self, source_path: str) -> None:
        """SFTP Copy file from watch folder to a destination folder on remote server.
        """

        try:

            destination_path = str(pathlib.Path(
                self.handler_config["destination"]) / source_path[len(self.handler_config["source"])+1:])

            with pysftp.Connection(self.handler_config["server"], username=self.handler_config["user"],
                                   password=self.handler_config["password"]) as sftp:
                if os.path.isfile(source_path):
                    sftp.put(source_path, destination_path)
                else:
                    sftp.makedirs(destination_path)

            logging.info("Uploaded file %s to %s",
                         source_path, destination_path)

            if self.handler_config["deletesource"]:
                os.remove(source_path)

        except (pysftp.ConnectionException, pysftp.AuthenticationException) as error:
            raise SFTPCopyFileHandlerError(error) from error
