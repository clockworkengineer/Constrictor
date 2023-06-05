import pytest
import pathlib
import tempfile

from tests.common import create_test_file
from core.constants import CONFIG_NAME, CONFIG_TYPE, CONFIG_SOURCE, CONFIG_DESTINATION, CONFIG_DELETESOURCE, CONFIG_EXITONFAILURE
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.error import FPEError
from builtin.copyfile_handler import CopyFileHandler


@pytest.fixture()
def copyfile_fixture() -> ConfigDict:

    config: ConfigDict = {CONFIG_NAME: "Copy File 1", CONFIG_TYPE: "CopyFile"}
    with tempfile.TemporaryDirectory() as directory_name:
        config[CONFIG_SOURCE] = str(pathlib.Path(directory_name) / "source")
        config[CONFIG_DESTINATION] = str(
            pathlib.Path(directory_name) / "destination")
        yield config


class TestBuiltinCopyFileHandler:

    def test_builtin_copyfile_handler_pass_none_as_config(self) -> None:
        with pytest.raises(FPEError):
            handdler: IHandler = CopyFileHandler(None)  # type: ignore

    def test_buitin_handler_create_non_existant_source(self, copyfile_fixture: ConfigDict) -> None:
        pathlib.Path(copyfile_fixture[CONFIG_DESTINATION]).mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(copyfile_fixture)
        assert pathlib.Path(copyfile_fixture[CONFIG_SOURCE]).exists()

    def test_buitin_handler_create_non_existant_destination(self, copyfile_fixture: ConfigDict) -> None:
        pathlib.Path(copyfile_fixture[CONFIG_SOURCE]).mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(copyfile_fixture)
        assert pathlib.Path(copyfile_fixture[CONFIG_DESTINATION]).exists()

    def test_buitin_handler_copy_a_single_source_to_destination(self, copyfile_fixture: ConfigDict) -> None:
        pathlib.Path(copyfile_fixture[CONFIG_SOURCE]).mkdir(
            parents=True,  exist_ok=True)
        handler = CopyFileHandler(copyfile_fixture)
        source_path = pathlib.Path(
            copyfile_fixture[CONFIG_SOURCE]) / "test.txt"
        destination_path = pathlib.Path(
            copyfile_fixture[CONFIG_DESTINATION]) / "test.txt"
        create_test_file(source_path)
        handler.process(source_path)
        assert destination_path.exists()
        assert source_path.exists()
