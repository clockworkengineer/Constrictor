"""SFTP Copy file handler."""


import logging
import os
import pysftp
from handler import Handler


class SFTPCopyFile(Handler):
    """SFTP Copy file/directories.

    SFTP Copy files created in watch folder to destination folder on remote SSH
    server keeping any in situ watch folder directory structure the same.

    Attributes:
        handler_name:  Name of handler object
        watch_folder:  Folder to watch for files
        ssh_server:    SSH Server
        ssh_user:      SSH Server user name
        ssh_password   SSH Server user password
        destination    Destination for copy
        recursive:     Boolean == true perform recursive file watch
        delete_source: Boolean == true delete source file on sucess
    """

    def __init__(self, handler_section):
        """ Intialise handler attributes and log details."""

        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.ssh_server = handler_section['server']
        self.ssh_user = handler_section['user']
        self.ssh_password = handler_section['password']
        self.destination_folder = handler_section['destination']
        self.recursive = handler_section['recursive']
        self.delete_source = handler_section['deletesource']

        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def process(self, event):
        """SFTP Copy file from watch folder to a destination folder on remote server."""

        destination_path = event.src_path[len(self.watch_folder) + 1:]
        destination_path = os.path.join(self.destination_folder,
                                        destination_path)

        with pysftp.Connection(self.ssh_server, username=self.ssh_user,
                               password=self.ssh_password) as sftp:
            if os.path.isfile(event.src_path):
                sftp.put(event.src_path, destination_path)
            else:
                sftp.makedirs(destination_path)

        logging.info('Uploaded file {} to {}'.format(
            event.src_path, destination_path))
        if self.delete_source:
            os.remove(event.src_path)
