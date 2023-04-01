"""CopyFile builtin handler.
"""

import os
import shutil
import logging
from ..handler import Handler


class CopyFileHandler(Handler):
    """Copy file/directories.

    Copy files created in watch folder to destination folder keeping any in 
    situ watch folder directory structure the same.

    Handler(Watcher) config values:
        name:           Name of handler object
        watch:          Folder to watch for files
        destination:    Destination for file copy
        recursive:      Boolean == true perform recursive file watch
        deletesource:   Boolean == true delete source file on success

    """

    def __init__(self, handler_config: dict[str, any]) -> None:
        """Initialise handler attributes.
        """
        self.handler_config = handler_config.copy()

    def process(self, event) -> None:
        """Copy file from watch folder to destination.
        """
        try:

            if self.handler_config["watch"][-1:] != "\\":
                self.handler_config["watch"] += "\\"
            if self.handler_config["destination"][-1:] != "\\":
                self.handler_config["destination"] += "\\"

            destination_path = event.src_path[len(
                self.handler_config["watch"]):]
            destination_path = os.path.join(self.handler_config["destination"],
                                            destination_path)

            if os.path.isfile(event.src_path):
                if not os.path.exists(os.path.dirname(destination_path)):
                    os.makedirs(os.path.dirname(destination_path))
                logging.info(
                    "Copying file %s to %s", event.src_path, destination_path)
                shutil.copy2(event.src_path, destination_path)

            elif os.path.isdir(event.src_path):
                if not os.path.exists(destination_path):
                    logging.info("Creating directory {event.src_path}")
                    os.makedirs(destination_path)

            if self.handler_config["deletesource"]:
                os.remove(event.src_path)

        except IOError as error:
            logging.error("Error in handler %s : %s",
                          self.handler_config["name"], error)
