import pytest
import tempfile
import pathlib

from core.handler import Handler


class TestCoreHandler:
    # Test Handler normalize path

    def test_core_handler_normalise_path(self) -> None:
        assert Handler.normalize_path(
            "./watcher/source") == str(pathlib.Path.cwd() / "watcher" / "source")

    # Test Handler create path

    def test_core_handler_create_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            temporary_directory_path: pathlib.Path = pathlib.Path(
                directory_name) / "watchers" / "source"
            assert not temporary_directory_path.exists()
            Handler.create_path(str(temporary_directory_path))
            assert temporary_directory_path.exists()
            temporary_directory_path.rmdir()

    # Test Handler create local destination
    # Test Handler setup path
