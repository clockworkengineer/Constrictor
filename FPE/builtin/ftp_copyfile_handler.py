"""FPE FTPCopyFile builtin handler.
"""


import pathlib
import logging
from ftplib import FTP

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.handler import Handler
from core.error import FPEError


class FTPCopyFileHandlerError(FPEError):
    """An error occurred in the FTPCopyFile handler.
    """

    def __init__(self, message) -> None:
        """FTPCopyFile handler error.

        Args:
            message (str): Exception message.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "FTPCopyFileHandler Error: " + self.message


class FTPCopyFileHandler(IHandler):
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

    def __init__(self, handler_config: ConfigDict) -> None:
        """Initialise handler attributes.

        Args:
            handler_config (ConfigDict): Handler configuration.

        Raises:
            FTPCopyFileHandlerError: None passed as handler configuration.
        """

        if handler_config is None:
            raise FTPCopyFileHandlerError("None passed as handler config.")

        self.handler_config = handler_config.copy()

        Handler.setup_path(self.handler_config, CONFIG_SOURCE)

        self.handler_config[CONFIG_DESTINATION] = Handler.normalize_path(
            self.handler_config[CONFIG_DESTINATION])

        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def process(self,  source_path: pathlib.Path) -> bool:
        """SFTP Copy file from source(watch) directory to a destination directory on remote server.

        Args:
            source_path (pathlib.Path): Source file path.

        Raises:
            FTPCopyFileHandlerError: Ann error occured while tryinhg to transfer file to FTP server.
        """

        try:

            destination_path: pathlib.Path = Handler.create_local_destination(
                source_path, self.handler_config)

            # with pysftp.Connection(self.handler_config["server"], username=self.handler_config["user"],
            #                        password=self.handler_config["password"]) as sftp:
            #     if source_path.is_file():
            #         sftp.put(source_path, destination_path)
            #     else:
            #         sftp.makedirs(destination_path)
            
            with FTP(host=self.handler_config["server"], user=self.handler_config["user"], passwd=self.handler_config["password"]) as ftp:
                if source_path.is_file():
                    with open(source_path, 'rb') as file:
                        ftp.storbinary(f'STOR {source_path.name}', file)
            #     else:
            #         sftp.makedirs(destination_path)

            logging.info("Uploaded file %s to %s",
                         source_path, destination_path)

            return True

        except (Exception) as error:
            if self.handler_config['exitonfailure']:
                raise FTPCopyFileHandlerError(str(error)) from error
            else:
                logging.info(FTPCopyFileHandlerError(error))

        return False
