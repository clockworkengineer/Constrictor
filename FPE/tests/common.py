import pathlib
import os
import tempfile
import shutil

from core.constants import CONFIG_TYPE, CONFIG_NAME, CONFIG_SOURCE, CONFIG_DESTINATION, CONFIG_EXITONFAILURE
from core.handler import Handler
from core.config import ConfigDict


def json_file_source(source_file: str) -> str:
    return str(pathlib.Path.cwd() / "FPE" / "tests" / "json" / source_file)


def create_test_file(source_path: pathlib.Path, read_only: bool = False) -> None:
    if not source_path.parent.exists():
        Handler.create_path(source_path.parent)
    with open(source_path, 'wb') as test_file:
        test_file.write(os.urandom(1024 * 1024))
    if read_only:
        source_path.chmod(0o444)


def create_watcher_config() -> ConfigDict:
    config: ConfigDict = {CONFIG_NAME: "Copy File", CONFIG_TYPE: "CopyFile", CONFIG_EXITONFAILURE :  True}
    with tempfile.TemporaryDirectory() as directory_name:
        config[CONFIG_SOURCE] = str(pathlib.Path(
            directory_name) / "source")
        config[CONFIG_DESTINATION] = str(pathlib.Path(
            directory_name) / "destination")
        return config
    
def remove_source_destination(watcher_config: ConfigDict) -> None:
    if CONFIG_SOURCE in watcher_config and pathlib.Path(watcher_config[CONFIG_SOURCE]).exists():
        shutil.rmtree(watcher_config[CONFIG_SOURCE])
    if CONFIG_DESTINATION in watcher_config and pathlib.Path(watcher_config[CONFIG_DESTINATION]).exists():
        shutil.rmtree(watcher_config[CONFIG_DESTINATION])
