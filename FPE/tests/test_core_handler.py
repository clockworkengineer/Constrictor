"""TEST"""
# pylint: disable=missing-function-docstring, missing-class-docstring


import tempfile
import pathlib
import pytest

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION
from core.config import ConfigDict
from core.handler import Handler


class TestCoreHandler:
    def test_core_handler_normalise_path(self) -> None:
        assert Handler.normalize_path("./watcher/source") == str(
            pathlib.Path.cwd() / "watcher" / "source"
        )

    def test_core_handler_create_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            temporary_directory_path: pathlib.Path = (
                pathlib.Path(directory_name) / "source"
            )
            assert not temporary_directory_path.exists()
            Handler.create_path(temporary_directory_path)
            assert temporary_directory_path.exists()
            temporary_directory_path.rmdir()

    def test_core_handler_create_local_destination(self) -> None:
        config: ConfigDict = {}
        source_path: pathlib.Path = pathlib.Path(
            Handler.normalize_path("./watcher/source")
        )
        destination_path: pathlib.Path = pathlib.Path(
            Handler.normalize_path("./watcher/destination")
        )
        source_file_path: pathlib.Path = source_path / "dir1" / "dir2" / "source.txt"
        config[CONFIG_SOURCE] = str(source_path)
        config[CONFIG_DESTINATION] = str(destination_path)
        assert (
            pathlib.Path(config[CONFIG_DESTINATION])
            / Handler.create_relative_source(source_file_path, config[CONFIG_SOURCE])
            == destination_path / "dir1" / "dir2" / "source.txt"
        )

    def test_core_handler_setup_path_doesnt_exist(self) -> None:
        config: ConfigDict = {CONFIG_SOURCE: "./watcher/source"}
        source_path: pathlib.Path = pathlib.Path(config[CONFIG_SOURCE])
        if source_path.exists():
            source_path.rmdir()
        _ = Handler.setup_path(config[CONFIG_SOURCE])
        assert source_path.exists()
        source_path.rmdir()

    def test_core_handler_setup_path_does_exist(self) -> None:
        config: ConfigDict = {CONFIG_SOURCE: "./watcher/source"}
        source_path: pathlib.Path = pathlib.Path(config[CONFIG_SOURCE])
        source_path.mkdir(parents=True, exist_ok=True)
        assert source_path.exists()
        _ = Handler.setup_path(config[CONFIG_SOURCE])
        assert source_path.exists()
        source_path.rmdir()

    def test_core_handler_setup_path_with_invalid_config_key(self) -> None:
        config: ConfigDict = {CONFIG_SOURCE: "./watcher/source"}
        with pytest.raises(KeyError):
            _ = Handler.setup_path(config[CONFIG_DESTINATION])
