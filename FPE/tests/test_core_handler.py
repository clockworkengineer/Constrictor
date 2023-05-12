import pytest
import tempfile
import pathlib
from typing import Any

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION
from core.handler import Handler


class TestCoreHandler:

    def test_core_handler_normalise_path(self) -> None:
        assert Handler.normalize_path(
            "./watcher/source") == str(pathlib.Path.cwd() / "watcher" / CONFIG_SOURCE)

    def test_core_handler_create_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            temporary_directory_path: pathlib.Path = pathlib.Path(
                directory_name) / "watcher" / CONFIG_SOURCE
            assert not temporary_directory_path.exists()
            Handler.create_path(temporary_directory_path)
            assert temporary_directory_path.exists()
            temporary_directory_path.rmdir()

    def test_core_handler_create_local_destination(self) -> None:
        config: dict[str, Any] = {}
        source_path: pathlib.Path = pathlib.Path(
            Handler.normalize_path("./watcher/source"))
        destination_path: pathlib.Path = pathlib.Path(
            Handler.normalize_path("./watcher/destination"))
        source_file_path: pathlib.Path = source_path / "dir1" / "dir2" / "source.txt"
        config[CONFIG_SOURCE] = str(source_path)
        config[CONFIG_DESTINATION] = str(destination_path)
        assert Handler.create_local_destination(
            source_file_path, config) == destination_path / "dir1" / "dir2" / "source.txt"

    def test_core_handler_setup_path_doesnt_exist(self) -> None:
        config: dict[str, Any] = {}
        config[CONFIG_SOURCE] = "./watcher/source"
        source_path: pathlib.Path = pathlib.Path(config[CONFIG_SOURCE])
        if source_path.exists():
            source_path.rmdir()
        Handler.setup_path(config, CONFIG_SOURCE)
        assert source_path.exists()
        source_path.rmdir()

    def test_core_handler_setup_path_does_exist(self) -> None:
        config: dict[str, Any] = {}
        config[CONFIG_SOURCE] = "./watcher/source"
        source_path: pathlib.Path = pathlib.Path(config[CONFIG_SOURCE])
        source_path.mkdir(parents=True, exist_ok=True)
        assert source_path.exists()
        Handler.setup_path(config, CONFIG_SOURCE)
        assert source_path.exists()
        source_path.rmdir()

    def test_core_handler_setup_path_with_invalid_config_key(self) -> None:
        config: dict[str, Any] = {}
        config[CONFIG_SOURCE] = "./watcher/source"
        source_path: pathlib.Path = pathlib.Path(config[CONFIG_SOURCE])
        with pytest.raises(KeyError):
            Handler.setup_path(config, CONFIG_DESTINATION)
