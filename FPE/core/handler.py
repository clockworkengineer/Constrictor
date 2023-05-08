"""Watcher file handler.

Protocol class that defines the file watcher handler interface.

"""

import errno
import pathlib
import logging
from typing import Protocol, Any


class IHandler(Protocol):
    """Interface for watcher file handler.
    """

    handler_config: dict[str, Any]  # Handler config dictionary

    def process(self, source_path: pathlib.Path) -> None:
        """Perform watcher file processing.

        Args:
            source_path (pathlib.Path): _description_

        Returns:
            _type_: _description_
        """


class Handler():
    """_summary_

    Returns:
        _type_: _description_
    """
    @staticmethod
    def normalize_path(path_to_normalise: str) -> str:
        """_summary_

        Args:
            path_to_normalise (str): _description_

        Returns:
            str: _description_
        """
        return str(pathlib.Path(path_to_normalise).absolute())

    @staticmethod
    def create_path(directory_path: pathlib.Path) -> None:
        """_summary_

        Args:
            directory_path (pathlib.Path): _description_
        """
        if not directory_path.exists():
            directory_path.mkdir(parents=True,  exist_ok=True)
            logging.info("Created directory %s.", directory_path)

    @staticmethod
    def create_local_destination(source_path: pathlib.Path, config: dict[str, Any]) -> pathlib.Path:
        """_summary_

        Args:
            source_path (pathlib.Path): _description_
            config (dict[str, Any]): _description_

        Returns:
            pathlib.Path: _description_
        """
        return pathlib.Path(
            config["destination"]) / str(source_path)[len(config["source"])+1:]

    @staticmethod
    def setup_path(handler_config: dict[str, Any], path_type: str) -> None:
        """_summary_

        Args:
            handler_config (dict[str, Any]): _description_
            path_type (str): _description_
        """
        handler_config[path_type] = Handler.normalize_path(
            handler_config[path_type])
        Handler.create_path(pathlib.Path(handler_config[path_type]))

    @staticmethod
    def wait_for_copy_completion(source_path: pathlib.Path) -> None:
        """_summary_

        Args:
            source_path (pathlib.Path): _description_
        """
        failure: bool = True
        while failure:
            try:
                with open(source_path, "rb") as source_file:
                    _ = source_file.read()
                failure = False
            except IOError as error:
                if error.errno == errno.EACCES:
                    pass
                else:
                    failure = False
