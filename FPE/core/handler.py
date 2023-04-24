"""Watcher file handler.

Protocol class that defines the file watcher handler interface.

"""

import pathlib
import logging
from typing import Protocol, Any


class Handler(Protocol):
    """Watcher file handler class"""

    handler_config: dict[str, Any]  # Handler config dictionary

    def process(self, source_path: str) -> None:
        """Perform watcher file processing.
        """

    @staticmethod
    def normalize_path(path_to_normalise: str) -> str:
        
        return str(pathlib.Path(path_to_normalise).absolute())

    @staticmethod
    def create_path(path_to_directory: str) -> None:
        
        with pathlib.Path(path_to_directory) as directory_path:
            if not directory_path.exists():
                directory_path.mkdir(parents=True,  exist_ok=True)
                logging.info("Created directory %s.", path_to_directory)

    @staticmethod
    def create_local_destination(source_path: str, config: dict[str, Any]) -> str:
        
        return str(pathlib.Path(
            config["destination"]) / source_path[len(config["source"])+1:])

    @staticmethod
    def setup_path(handler_config: dict[str, Any], path_type: str):
        
        handler_config[path_type] = Handler.normalize_path(
            handler_config[path_type])
        Handler.create_path(handler_config[path_type])
        
