"""FPE File handler.

Handler utility static methods.

"""

import errno
import pathlib
import logging

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION
from core.config import ConfigDict


class Handler():
    """Directory watcher handler utility static methods.

    Returns:
        _type_: _description_
    """
    @staticmethod
    def normalize_path(path_to_normalise: str) -> str:
        """Normalise passed in path string.

        Args:
            path_to_normalise (str): Path string.

        Returns:
            str: Normalised path string.
        """
        return str(pathlib.Path(path_to_normalise).absolute())

    @staticmethod
    def create_path(directory_path: pathlib.Path) -> None:
        """Create directory for path if it does not exist.

        Args:
            directory_path (pathlib.Path): Directory path.
        """
        if not directory_path.exists():
            directory_path.mkdir(parents=True,  exist_ok=True)
            logging.info("Created directory %s.", directory_path)

    @staticmethod
    def create_local_destination(source_path: pathlib.Path, config: ConfigDict) -> pathlib.Path:
        """Create local desination for source file.

        Args:
            source_path (pathlib.Path): Soure file path.
            config (ConfigDict): Watcher handler config.

        Returns:
            pathlib.Path: _description_
        """
        return pathlib.Path(
            config[CONFIG_DESTINATION]) / str(source_path)[len(config[CONFIG_SOURCE])+1:]

    @staticmethod
    def setup_path(handler_config: ConfigDict, path_type: str) -> None:
        """_summary_

        Args:
            handler_config (ConfigDict): Watcher handler config.
            path_type (str): Watcher handler type.
        """
        handler_config[path_type] = Handler.normalize_path(
            handler_config[path_type])
        Handler.create_path(pathlib.Path(handler_config[path_type]))

    @staticmethod
    def wait_for_copy_completion(source_path: pathlib.Path) -> None:
        """_summary_

        Args:
            source_path (pathlib.Path):  Soure file path.
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
