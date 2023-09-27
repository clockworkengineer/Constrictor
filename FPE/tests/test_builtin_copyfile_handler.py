"""TEST"""


import pathlib
import pytest

from tests.common import (
    create_test_file,
    create_copyfile_config,
    remove_source_destination,
)
from core.constants import CONFIG_SOURCE, CONFIG_DESTINATION
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.error import FPEError
from builtin.copyfile_handler import CopyFileHandler


@pytest.fixture(name="generate_copyfile_config")
def fixture_generate_copyfile_config() -> ConfigDict:
    copyfile_config: ConfigDict = create_copyfile_config()

    yield copyfile_config

    remove_source_destination(copyfile_config)


class TestBuiltinCopyFileHandler:
    def test_builtin_copyfile_handler_pass_none_as_config(self) -> None:
        with pytest.raises(FPEError):
            _: IHandler = CopyFileHandler(None)  # type: ignore

    def test_buitin_handler_create_non_existant_source(
        self, generate_copyfile_config: ConfigDict
    ) -> None:
        pathlib.Path(generate_copyfile_config[CONFIG_DESTINATION]).mkdir(
            parents=True, exist_ok=True
        )
        _: IHandler = CopyFileHandler(generate_copyfile_config)
        assert pathlib.Path(generate_copyfile_config[CONFIG_SOURCE]).exists()

    def test_buitin_handler_create_non_existant_destination(
        self, generate_copyfile_config: ConfigDict
    ) -> None:
        pathlib.Path(generate_copyfile_config[CONFIG_SOURCE]).mkdir(
            parents=True, exist_ok=True
        )
        _: IHandler = CopyFileHandler(generate_copyfile_config)
        assert pathlib.Path(generate_copyfile_config[CONFIG_DESTINATION]).exists()

    def test_buitin_handler_copy_a_single_source_to_destination(
        self, generate_copyfile_config: ConfigDict
    ) -> None:
        pathlib.Path(generate_copyfile_config[CONFIG_SOURCE]).mkdir(
            parents=True, exist_ok=True
        )
        handler = CopyFileHandler(generate_copyfile_config)
        source_path = pathlib.Path(generate_copyfile_config[CONFIG_SOURCE]) / "test.txt"
        destination_path = (
            pathlib.Path(generate_copyfile_config[CONFIG_DESTINATION]) / "test.txt"
        )
        create_test_file(source_path)
        handler.process(source_path)
        assert destination_path.exists()
        assert source_path.exists()
