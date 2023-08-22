"""FPE File handler interface.

Protocol class that defines the file handler interface.

"""

import pathlib
from typing import Protocol

from core.config import ConfigDict
from core.constants import (
    CONFIG_NAME,
    CONFIG_SOURCE,
    CONFIG_EXITONFAILURE,
    CONFIG_DELETESOURCE,
    CONFIG_RECURSIVE,
)

class IHandler(Protocol):
    """Interface for watcher file handler."""

    name : str = ""
    source: str = ""
    recursive: bool = False
    exit_on_failure: bool = False
    delete_source: bool = True
    files_processed: int = 0

    def process(self, source_path: pathlib.Path) -> bool:
        """Perform watcher file processing.

        Args:
            source_path (pathlib.Path): Source fiel path.
        """

    def set_mandatory_config(self, handler_config: ConfigDict) -> None:
        """_summary_

        Args:
            handler_config (ConfigDict): _description_
        """
        self.name = handler_config[CONFIG_NAME]
        self.source = handler_config[CONFIG_SOURCE]
        self.exit_on_failure = handler_config[CONFIG_EXITONFAILURE]
        self.recursive = handler_config[CONFIG_RECURSIVE]
        self.delete_source = handler_config[CONFIG_DELETESOURCE]