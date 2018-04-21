"""SFTP Copy file handler."""

from common import _display_details
import logging
import os
import paramiko
from watchdog.events import FileSystemEventHandler

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class SFTPCopyFile(FileSystemEventHandler):
    """SFTP Copy file/directories.
    
    SFTP Copy files created in watch folder to destination folder on remote SSH
    server keeping any in situ watch folder directory structure the same.
    
    Attributes:
    handler_name:  Name of handler object
    watch_folder:  Folder to watch for files
 
    """
    
    def __init__(self, handler_section):
        """ Intialise handler attributes and log details."""
        
        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.ssh_server = handler_section['server']
        self.ssh_user = handler_section['user']
        self.ssh_userpassword = handler_section['password']
        self.destination_folder = handler_section['destination']
        self.recursive = handler_section['recursive']
        self.delete_source = handler_section['deletesource']
        
        _display_details(handler_section)
         
    def on_created(self, event):
        """SFTP Copy file from watch folder to a destination folder on remote server."""
        pass
