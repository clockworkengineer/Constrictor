"""Watcher file handler.

Protocol class that defines the file watcher handler interface.

"""

import pathlib
from typing import Protocol, Any


class Handler(Protocol):
    """Watcher file handler class"""

    handler_config: dict[str, Any]  # Handler config dictionary

    def process(self, source_path: str) -> None:
        """Perform watcher file processing.
        """

    @staticmethod
    def normalize_path(path: str):
        path = str(pathlib.Path(path).resolve())

    @staticmethod
    def create_path(path: str):
        pathlib.Path(path).resolve().mkdir(parents=True,  exist_ok=True)
        
    @staticmethod
    def create_local_destination(source_path : str, destination_path: str, config : dict[str, Any]) -> str:
        return str(pathlib.Path(
                config["destination"]) / source_path[len(config["source"])+1:])

