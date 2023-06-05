import pytest
import time
import pathlib
import tempfile

from tests.common import create_test_file
from core.constants import CONFIG_TYPE, CONFIG_NAME, CONFIG_SOURCE, CONFIG_DESTINATION, CONFIG_DELETESOURCE, CONFIG_EXITONFAILURE
from core.config import ConfigDict
from core.watcher import Watcher, WatcherError
from core.factory import Factory
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler


@pytest.fixture()
def watcher_fixture() -> ConfigDict:

    Factory.clear()
    Factory.register("CopyFile", CopyFileHandler)
    Factory.register("SFTPCopyFile", SFTPCopyFileHandler)

    config: ConfigDict = {CONFIG_NAME: "Copy File 1", CONFIG_TYPE: "CopyFile"}
    with tempfile.TemporaryDirectory() as directory_name:
        config[CONFIG_SOURCE] = str(pathlib.Path(
            directory_name) / "source")
        config[CONFIG_DESTINATION] = str(pathlib.Path(
            directory_name) / "destination")
        yield config


class TestCoreWatcher:

    def __copy_count_files(self, watcher_fixture, count) -> None:
        watcher = Watcher(watcher_fixture)
        watcher.start()
        source_path = pathlib.Path(watcher_fixture[CONFIG_SOURCE])
        destination_path = pathlib.Path(watcher_fixture[CONFIG_DESTINATION])
        for file_number in range(count):
            create_test_file(source_path / f"test{file_number}.txt")
        while watcher.files_processed < count:
            time.sleep(0.01)
        for file_number in range(count):
            assert (
                source_path / f"test{file_number}.txt").exists() != watcher_fixture[CONFIG_DELETESOURCE]
            assert (destination_path /
                    f"test{file_number}.txt").exists() == True
        watcher.stop()

    def test_watcher_with_config_of_none(self):
        with pytest.raises(WatcherError):
            _ = Watcher(None)

    def test_watcher_inlaid_config(self, watcher_fixture: ConfigDict):
        watcher_fixture.pop(CONFIG_DESTINATION)
        with pytest.raises(WatcherError):
            _ = Watcher(watcher_fixture)

    def test_watcher_with_a_valid_config(self, watcher_fixture: ConfigDict):
        watcher = Watcher(watcher_fixture)
        assert watcher != None

    def test_watcher_with_a_valid_config_check_source_directory(self, watcher_fixture: ConfigDict):
        assert pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]).exists() == False
        watcher = Watcher(watcher_fixture)
        assert pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]).exists() == True

    def test_watcher_with_a_valid_config_check_desination_directory(self, watcher_fixture: ConfigDict):
        assert pathlib.Path(
            watcher_fixture[CONFIG_DESTINATION]).exists() == False
        watcher = Watcher(watcher_fixture)
        assert pathlib.Path(
            watcher_fixture[CONFIG_DESTINATION]).exists() == True

    def test_watcher_initial_state_stopped(self, watcher_fixture: ConfigDict):
        watcher = Watcher(watcher_fixture)
        assert watcher.is_running == False

    def test_watcher_started(self, watcher_fixture: ConfigDict):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_start_a_running_watcher(self, watcher_fixture: ConfigDict):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_stopping_a_stopped_watcher(self, watcher_fixture: ConfigDict):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        watcher.stop()
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped(self, watcher_fixture: ConfigDict):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped_then_restarted(self, watcher_fixture: ConfigDict):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_copy_a_single_file_from_source_to_destination(self, watcher_fixture: ConfigDict):
        self.__copy_count_files(watcher_fixture, 1)

    def test_watcher_copy_a_single_file_from_source_to_destination_with_deletesource_false(self, watcher_fixture: ConfigDict):
        watcher_fixture[CONFIG_DELETESOURCE] = False
        self.__copy_count_files(watcher_fixture, 1)

    def test_watcher_copy_ten_files_from_source_to_destination(self, watcher_fixture: ConfigDict):
        self.__copy_count_files(watcher_fixture, 10)

    def test_watcher_copy_fifty_files_from_source_to_destination(self, watcher_fixture: ConfigDict):
        self.__copy_count_files(watcher_fixture, 50)

    def test_watcher_copy_onehundred_files_from_source_to_destination(self, watcher_fixture: ConfigDict):
        self.__copy_count_files(watcher_fixture, 100)

    def test_watcher_copy_onethousand_files_from_source_to_destination(self, watcher_fixture: ConfigDict):
        self.__copy_count_files(watcher_fixture, 1000)

