import pathlib
import os
import tempfile

from core.constants import CONFIG_TYPE, CONFIG_NAME, CONFIG_SOURCE, CONFIG_DESTINATION
from core.handler import Handler
from core.config import ConfigDict


def json_file_source(source_file: str) -> str:
    return str(pathlib.Path.cwd() / "FPE" / "tests" / "json" / source_file)


def create_test_file(source_path: pathlib.Path) -> None:
    if not source_path.parent.exists():
        Handler.create_path(source_path.parent)
    with open(source_path, 'wb') as test_file:
        test_file.write(os.urandom(1024 * 1024))
        
def create_watcher_config() -> ConfigDict:
    config: ConfigDict = {CONFIG_NAME: "Copy File", CONFIG_TYPE: "CopyFile"}
    with tempfile.TemporaryDirectory() as directory_name:
        config[CONFIG_SOURCE] = str(pathlib.Path(
            directory_name) / "source")
        config[CONFIG_DESTINATION] = str(pathlib.Path(
            directory_name) / "destination")
        return config
