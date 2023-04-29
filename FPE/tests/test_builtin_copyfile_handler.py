import pytest
import pathlib
import shutil
import tempfile
from typing import Any

from core.error import FPEError
from core.handler import Handler
from builtin.copyfile_handler import CopyFileHandler, CopyFileHandlerError


class Fixture:
    source_path: pathlib.Path
    destination_path: pathlib.Path
    config: dict[str, Any] = {}


@pytest.fixture()
def setup_source_destination() -> Fixture:
    fixture: Fixture = Fixture()
    with tempfile.TemporaryDirectory() as directory_name:
        fixture.source_path = pathlib.Path(
            directory_name) / "watchers" / "source"
        fixture.destination_path = pathlib.Path(
            directory_name) / "watchers" / "destination"
        if fixture.source_path.exists():
            fixture.source_path.rmdir()
        if fixture.destination_path.exists():
            fixture.destination_path.rmdir()
        fixture.config["source"] = str(fixture.source_path)
        fixture.config["destination"] = str(fixture.destination_path)
        fixture.config["deletesource"] = False
        fixture.config["recursive"] = True
        fixture.config["exitonfailure"] = True
    yield fixture
    shutil.rmtree(fixture.source_path)
    shutil.rmtree(fixture.destination_path)


class TestBuiltinCopyFileHandler:

    def test_builtin_copyfile_handler_pass_none_as_config(self) -> None:
        with pytest.raises(FPEError):
            handdler: Handler = CopyFileHandler(None)  # type: ignore

    def test_buitin_handler_create_non_existant_source(self, setup_source_destination) -> None:
        setup_source_destination.destination_path.mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(setup_source_destination.config)
        assert setup_source_destination.source_path.exists()

    def test_buitin_handler_create_non_existant_destination(self, setup_source_destination) -> None:
        setup_source_destination.source_path.mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(setup_source_destination.config)
        assert setup_source_destination.destination_path.exists()

    def test_buitin_handler_copy_a_single_source_to_destination(self, setup_source_destination) -> None:
        setup_source_destination.source_path.mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(setup_source_destination.config)
        source_file = setup_source_destination.source_path / "test.txt"
        destination_file = setup_source_destination.destination_path / "test.txt"
        source_file.touch()
        assert not destination_file.exists()
        handler.process(str(source_file))
        assert destination_file.exists()
        assert source_file.exists()

    def test_buitin_handler_copy_a_single_source_file_to_destination_deleting_source(self, setup_source_destination) -> None:
        setup_source_destination.source_path.mkdir(
            parents=True,  exist_ok=True)
        setup_source_destination.config["deletesource"] = True
        handler = CopyFileHandler(setup_source_destination.config)
        source_file = setup_source_destination.source_path / "test.txt"
        destination_file = setup_source_destination.destination_path / "test.txt"
        source_file.touch()
        assert not destination_file.exists()
        handler.process(str(source_file))
        assert destination_file.exists()
        assert not source_file.exists()

    def test_buitin_handler_copy_source_directory_structure_to_destination(self, setup_source_destination) -> None:
        (setup_source_destination.source_path / "dir1" / "dir2" / "dir3").mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(setup_source_destination.config)
        source_file = setup_source_destination.source_path / \
            "dir1" / "dir2" / "dir3" / "test.txt"
        destination_file = setup_source_destination.destination_path / \
            "dir1" / "dir2" / "dir3" / "test.txt"
        source_file.touch()
        assert not destination_file.exists()
        handler.process(str(source_file))
        assert destination_file.exists()
        assert source_file.exists()

    def test_buitin_handler_copy_source_directory_structure_to_destination_deleting_source(self, setup_source_destination) -> None:
        (setup_source_destination.source_path / "dir1" / "dir2" / "dir3").mkdir(
            parents=True,  exist_ok=True)
        setup_source_destination.config["deletesource"] = True
        handler = CopyFileHandler(setup_source_destination.config)
        source_file = setup_source_destination.source_path / \
            "dir1" / "dir2" / "dir3" / "test.txt"
        destination_file = setup_source_destination.destination_path / \
            "dir1" / "dir2" / "dir3" / "test.txt"
        source_file.touch()
        assert not destination_file.exists()
        handler.process(str(source_file))
        assert destination_file.exists()
        assert not source_file.exists()
