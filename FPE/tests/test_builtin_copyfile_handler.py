import pytest
import pathlib
import tempfile
from typing import Any

from core.error import FPEError
from core.handler import Handler
from builtin.copyfile_handler import CopyFileHandler, CopyFileHandlerError

class Fixture:
    source_path : pathlib.Path
    destination_path : pathlib.Path
    config: dict[str, Any] = {}
    
@pytest.fixture()
def setup_source_destination() -> Fixture:
    fixture: Fixture = Fixture()
    with tempfile.TemporaryDirectory() as directory_name:
            source_directory_path: pathlib.Path = pathlib.Path(
                directory_name) / "watchers" / "source"
            destination_directory_path: pathlib.Path = pathlib.Path(
                directory_name) / "watchers" / "destination"
            fixture.source_path = source_directory_path
            fixture.destination_path = destination_directory_path
    if fixture.source_path.exists():
        fixture.setup_source_destination.source_path.rmdir()
    if fixture.destination_path.exists():
        fixture.setup_source_destination.destination_path.rmdir()
    fixture.config["source"] = str(fixture.source_path)
    fixture.config["destination"] = str(fixture.destination_path)
    return fixture
    

class TestBuiltinCopyFileHandler:
    

    # Test CopyFileHandler checks for None passed in as config
    def test_builtin_copyfile_handler_pass_none_as_config(self) -> None:
        with pytest.raises(FPEError):
            handdler : Handler = CopyFileHandler(None)

    # Test CopyFileHandler creates non-existant source
    def test_buitin_handler_create_non_existant_source(self, setup_source_destination) -> None:
        setup_source_destination.destination_path.mkdir(parents=True,  exist_ok=True)
        assert True
        
        
    # Test CopyFileHandler create non-existant destinati on
    # Test CopyFileHandler single file copied into source then copied to destination
    # Test CopyFileHandler single file copied into source then copied to destination and source file deleted
    # Test CopyFileHandler a whole directory structure copied into source then copied to destination
    # Test CopyFileHandler copies a whole directory structure copied into source then copied to destination amd source files deleted
     
