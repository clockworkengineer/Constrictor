"""FPE File handler.

Handler utility static methods.

"""


import os
import errno
import pathlib
import logging
from decouple import config

from core.constants import (
    CONFIG_NAME,
    CONFIG_SOURCE,
    CONFIG_EXITONFAILURE,
    CONFIG_DELETESOURCE,
    CONFIG_RECURSIVE,
)
from core.config import ConfigDict
from core.interface.ihandler import IHandler


class Handler:
    """Directory watcher handler utility static methods."""

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
            directory_path.mkdir(parents=True, exist_ok=True)
            logging.info("Created directory %s.", directory_path)

    @staticmethod
    def create_relative_source(source_path: str, source_root: str) -> str:
        """Create source path relative to the source root.

        Args:
            source_path (str): Source path.
            source_root (str): Source root.

        Returns:
            str: Relative source path.
        """
        return str(source_path)[len(source_root) + 1 :]

    @staticmethod
    def setup_path(directory_path: str) -> None:
        """Setup directory to be used by handler.

        Args:
            handler_config (ConfigDict): Watcher handler config.
            path_type (str): Watcher handler type.
        """
        directory_path = Handler.normalize_path(directory_path)
        Handler.create_path(pathlib.Path(directory_path))

    @staticmethod
    def wait_for_copy_completion(source_path: pathlib.Path) -> None:
        """Wait for file copy to be completed.

        Args:
            source_path (pathlib.Path):  Source file path.
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
        """Remove source file plus any empty directories its deletion creates.

        Args:
            root_path (pathlib.Path): Root path.
            source_path (pathlib.Path): Source file path.
        """
        source_path.unlink()
        while source_path.parent != root_path:
            if len(os.listdir(source_path.parent)) == 0:
                source_path.parent.chmod(source_path.parent.stat().st_mode | 0o664)
                source_path.parent.rmdir()
                source_path = source_path.parent
                continue
            break

    @staticmethod
    def get_config(handler_config: ConfigDict, attribute: str) -> any:
        """Get an attribute from config otherwise if it is "" get from
        environment variable config["name"] + attribute.

        Args:
            handler_config (ConfigDict): handler config.
            attribute (str): Attribute name.

        Returns:
            any: Return attribute.
        """
        if handler_config[attribute] != "":
            return handler_config[attribute]

        value = config(handler_config[CONFIG_NAME] + " " + attribute)

        return value

    @staticmethod
    def set_mandatory_config(ihandler: IHandler, handler_config: ConfigDict) -> None:
        """_summary_

        Args:
            handler_config (ConfigDict): _description_
        """
        ihandler.name = handler_config[CONFIG_NAME]
        ihandler.source = handler_config[CONFIG_SOURCE]
        ihandler.exit_on_failure = handler_config[CONFIG_EXITONFAILURE]
        ihandler.recursive = handler_config[CONFIG_RECURSIVE]
        ihandler.delete_source = handler_config[CONFIG_DELETESOURCE]
