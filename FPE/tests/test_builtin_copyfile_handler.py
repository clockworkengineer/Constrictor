import pytest
import pathlib
import shutil
import tempfile
from typing import Any

from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION, CONFIG_DELETESOURCE
from core.error import FPEError
from core.handler import IHandler
from builtin.copyfile_handler import CopyFileHandler


class Fixture:
    source_path: pathlib.Path
    destination_path: pathlib.Path
    config: dict[str, Any] = {}


@pytest.fixture()
def setup_source_destination() -> Fixture:
    fixture: Fixture = Fixture()
    with tempfile.TemporaryDirectory() as directory_name:
        fixture.source_path = pathlib.Path(
            directory_name) / "watcher" / CONFIG_SOURCE
        fixture.destination_path = pathlib.Path(
            directory_name) / "watcher" / "destination"
        fixture.config[CONFIG_SOURCE] = str(fixture.source_path)
        fixture.config[CONFIG_DESTINATION] = str(fixture.destination_path)
        fixture.config[CONFIG_DELETESOURCE] = False
        fixture.config["exitonfailure"] = True
    yield fixture
    shutil.rmtree(fixture.source_path)
    shutil.rmtree(fixture.destination_path)


class TestBuiltinCopyFileHandler:

    def test_builtin_copyfile_handler_pass_none_as_config(self) -> None:
        with pytest.raises(FPEError):
            handdler: IHandler = CopyFileHandler(None)  # type: ignore

    def test_buitin_handler_create_non_existant_source(self, setup_source_destination: Fixture) -> None:
        setup_source_destination.destination_path.mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(setup_source_destination.config)
        assert setup_source_destination.source_path.exists()

    def test_buitin_handler_create_non_existant_destination(self, setup_source_destination: Fixture) -> None:
        setup_source_destination.source_path.mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(setup_source_destination.config)
        assert setup_source_destination.destination_path.exists()

    def test_buitin_handler_copy_a_single_source_to_destination(self, setup_source_destination: Fixture) -> None:
        setup_source_destination.source_path.mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(setup_source_destination.config)
        source_file = setup_source_destination.source_path / "test.txt"
        destination_file = setup_source_destination.destination_path / "test.txt"
        source_file.touch()
        handler.process(source_file)
        assert destination_file.exists()
        assert source_file.exists()

    def test_buitin_handler_copy_a_single_source_file_to_destination_deleting_source(self, setup_source_destination: Fixture) -> None:
        setup_source_destination.source_path.mkdir(
            parents=True,  exist_ok=True)
        setup_source_destination.config[CONFIG_DELETESOURCE] = True
        handler = CopyFileHandler(setup_source_destination.config)
        source_file = setup_source_destination.source_path / "test.txt"
        destination_file = setup_source_destination.destination_path / "test.txt"
        source_file.touch()
        handler.process(source_file)
        assert destination_file.exists()
        assert not source_file.exists()
