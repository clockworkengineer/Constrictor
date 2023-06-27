"""FPE File handler.

Handler utility static methods.

"""


import os
import errno
import pathlib
import logging

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION
from core.config import ConfigDict


class Handler():
    """Directory watcher handler utility static methods.
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
            pathlib.Path: Destination file path created from config and source file path.
        """
        return pathlib.Path(
            config[CONFIG_DESTINATION]) / str(source_path)[len(config[CONFIG_SOURCE])+1:]

    @staticmethod
    def setup_path(handler_config: ConfigDict, path_type: str) -> None:
        """Setup directory to be used by handler.

        Args:
            handler_config (ConfigDict): Watcher handler config.
            path_type (str): Watcher handler type.
        """
        handler_config[path_type] = Handler.normalize_path(
            handler_config[path_type])
        Handler.create_path(pathlib.Path(handler_config[path_type]))

    @staticmethod
    def wait_for_copy_completion(source_path: pathlib.Path) -> None:
        """Wait for file copy to be completed.

        Args:
            source_path (pathlib.Path):  Soure file path.
        """

        if source_path.is_file():
            failure: bool = True
            while failure:
                try:
                    with open(source_path, "rb") as file_path:
                        _ = file_path.read()
                    failure = False
                except IOError as error:
                    if error.errno == errno.EACCES:
                        pass
                    else:
                        failure = False

        source_path.chmod(source_path.stat().st_mode | 0o664)

    @staticmethod
    def remove_source(root_path: pathlib.Path, source_path: pathlib.Path):
        """_summary_

        Args:
            root_path (pathlib.Path): _description_
            source_path (pathlib.Path): _description_
        """
        source_path.unlink()
        while source_path.parent != root_path:
            if len(os.listdir(source_path.parent)) == 0:
                source_path.parent.chmod(
                    source_path.parent.stat().st_mode | 0o664)
                source_path.parent.rmdir()
                source_path = source_path.parent
                continue
            break
