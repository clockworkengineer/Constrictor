"""SFTPCopyFile builtin handler.
"""


import pathlib
import logging
from typing import Any
import pysftp

from core.constants import CONFIG_SOURCE
from core.handler import IHandler, Handler
from core.error import FPEError


class SFTPCopyFileHandlerError(FPEError):
    """An error occurred in the SFTPCopyFile handler.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "SFTPCopyFileHandler Error: " + str(self.message)


class SFTPCopyFileHandler(IHandler):
    """SFTP Copy file/directories.

    SFTP Copy files created in watch folder to destination folder on remote SSH server.

    Attributes:
        name:           Name of handler object
        source:         Folder to watch for files
        server:         SSH Server
        user:           SSH Server username
        password:       SSH Server user password
        destination:    Destination for copy
        deletesource:   Boolean == true delete source file on success
        exitonfailure:  Boolean == true exit handler on failure; generating an exception

    """

    def __init__(self, handler_config: dict[str, Any]) -> None:
        """ Initialise handler attributes.
        """

        if handler_config is None:
            raise SFTPCopyFileHandlerError("None passed as handler config.")

        self.handler_config = handler_config.copy()

        Handler.setup_path(self.handler_config, CONFIG_SOURCE)

        self.handler_config["destination"] = Handler.normalize_path(
            self.handler_config["destination"])

        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def process(self,  source_path: pathlib.Path) -> None:
        """SFTP Copy file from source(watch) directory to a destination directory on remote server.
        """

        try:

            destination_path: pathlib.Path = Handler.create_local_destination(
                source_path, self.handler_config)

            with pysftp.Connection(self.handler_config["server"], username=self.handler_config["user"],
                                   password=self.handler_config["password"]) as sftp:
                if source_path.is_file():
                    sftp.put(source_path, destination_path)
                else:
                    sftp.makedirs(destination_path)

            logging.info("Uploaded file %s to %s",
                         source_path, destination_path)

            if self.handler_config["deletesource"]:
                source_path.unlink()

        except (pysftp.ConnectionException, pysftp.AuthenticationException) as error:
            if self.handler_config['exitonfailure']:
                raise SFTPCopyFileHandlerError(error) from error
            else:
                logging.info(SFTPCopyFileHandlerError(error))
