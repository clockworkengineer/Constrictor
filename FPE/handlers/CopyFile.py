"""Copy file handler."""

import logging
import os
import shutil
from watchdog.events import FileSystemEventHandler
from handler_common import display_details


class CopyFile:
    """Copy file/directories.

    Copy files created in watch folder to destination folder keeping any in 
    situ watch folder directory structure the same.

    Attributes:
        handler_name:         Name of handler object
        watch_folder:         Folder to watch for files
        destination_folder:   Destination for file copy
        recursive:            Boolean == true perform recursive file watch
        delete_source:        Boolean == true delete source file on success
    """

    def __init__(self, handler_section):
        """ Initialise handler attributes and log details."""

        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.destination_folder = handler_section['destination']
        self.recursive = handler_section['recursive']
        self.delete_source = handler_section['deletesource']

        display_details(handler_section)

    def on_created(self, event):
        """Copy file from watch folder to destination."""
        try:

            destination_path = event.src_path[len(self.watch_folder) + 1:]
            destination_path = os.path.join(self.destination_folder,
                                            destination_path)

            if os.path.isfile(event.src_path):
                if not os.path.exists(os.path.dirname(destination_path)):
                    os.makedirs(os.path.dirname(destination_path))
                logging.info('Copying file {} to {}'.
                             format(event.src_path, destination_path))
                shutil.copy2(event.src_path, destination_path)

            elif os.path.isdir(event.src_path):
                if not os.path.exists(destination_path):
                    logging.info('Creating directory {}'.
                                 format(event.src_path))
                    os.makedirs(destination_path)

            if self.delete_source:
                os.remove(event.src_path)

        except Exception as e:
            logging.error("Error in handler {}: {}".
                          format(self.handler_name, e))
