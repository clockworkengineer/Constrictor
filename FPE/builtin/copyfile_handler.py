"""CopyFile builtin handler.
"""

import os
import shutil
import logging
from core.handler import Handler


class CopyFileHandlerError(Exception):
    """An error occured in the CopyFile handler.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return " CopyFileHandler Error: " + str(self.message)


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

    # handler_config : dict[str, any]

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

            destination_path = os.path.join(self.handler_config["destination"],
                                            event.src_path[len(
                                                self.handler_config["watch"]):])

            if os.path.isfile(event.src_path):
                logging.info(
                    "Copying file %s to %s", event.src_path, destination_path)
                shutil.copy2(event.src_path, destination_path)
                if self.handler_config["deletesource"]:
                    os.remove(event.src_path)

            elif os.path.isdir(event.src_path):
                if not os.path.exists(destination_path):
                    logging.info("Creating directory %s", event.src_path)
                    os.makedirs(destination_path)

        except (OSError, KeyError, ValueError) as error:
            raise CopyFileHandlerError(error) from error
