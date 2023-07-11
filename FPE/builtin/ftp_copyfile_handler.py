"""FPE FTPCopyFile builtin handler.
"""


import os
import pathlib
import logging
from ftplib import FTP, all_errors

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION, CONFIG_EXITONFAILURE, CONFIG_SERVER, CONFIG_USER, CONFIG_PASSWORD
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
    """FTP Copy file/directories.

    FTP Copy files created in watch folder to destination folder on remote FTP server.

    Attributes:
        name:           Name of handler object
        source:         Folder to watch for files
        server:         FTP Server
        user:           FTP Server username
        password:       FTP Server user password
        destination:    Destination for copy
        deletesource:   Boolean == true delete source file on success
        exitonfailure:  Boolean == true exit handler on failure; generating an exception

    """

    server: str = ""
    user: str = ""
    password: str = ""
    desination: str = ""
    exitonfailure :  bool = False

    def __init__(self, handler_config: ConfigDict) -> None:
        """Initialise handler attributes.

        Args:
            handler_config (ConfigDict): Handler configuration.

        Raises:
            FTPCopyFileHandlerError: None passed as handler configuration.
        """

        if handler_config is None:
            raise FTPCopyFileHandlerError("None passed as handler config.")

        Handler.setup_path(handler_config, CONFIG_SOURCE)

        self.destination = handler_config[CONFIG_DESTINATION]
        self.server = handler_config[CONFIG_SERVER]
        self.user = handler_config[CONFIG_USER]
        self.password = handler_config[CONFIG_PASSWORD]
        self.exitonfailure = handler_config[CONFIG_EXITONFAILURE]

    def __cwd_destination(self, ftp: FTP, destination: str) -> None:
        """_summary_

        Args:
            ftp (FTP): _description_
            destination (str): _description_
        """
        
        for directory in destination.split(os.sep):
            try:
                ftp.cwd(directory)
            except (all_errors):
                ftp.mkd(directory)
                ftp.cwd(directory)

    def process(self,  source_path: pathlib.Path) -> bool:
        """FTP Copy file from source(watch) directory to a destination directory on remote server.

        Args:
            source_path (pathlib.Path): Source file path.

        Raises:
            FTPCopyFileHandlerError: Ann error occured while tryinhg to transfer file to FTP server.
        """

        try:

            with FTP(host=self.server, user=self.user, passwd=self.password) as ftp:

                if self.desination != "":
                    self.__cwd_destination(ftp, self.destination)

                if source_path.is_file():
                    with open(source_path, 'rb') as file:
                        ftp.storbinary(f'STOR {source_path.name}', file)

                    logging.info("Uploaded file %s to server %s",
                                 source_path, self.server)

                    return True

            return False

        except (all_errors) as error:
            if self.exitonfailure:
                raise FTPCopyFileHandlerError(str(error)) from error
            else:
                logging.info(FTPCopyFileHandlerError(error))

        return False
