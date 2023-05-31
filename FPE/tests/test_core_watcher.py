import pytest
import time
import pathlib
import shutil
import tempfile

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
            directory_name) / "watcher" / "source")
        config[CONFIG_DESTINATION] = str(pathlib.Path(
            directory_name) / "watcher" / "destination")

    yield config

    shutil.rmtree(config[CONFIG_SOURCE])
    shutil.rmtree(config[CONFIG_DESTINATION])


class TestCoreWatcher:

    def test_watcher_with_config_of_none(self):
        with pytest.raises(WatcherError):
            _ = Watcher(None)

    def test_watcher_with_a_valid_config(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        assert watcher != None

    def test_watcher_with_a_valid_config_check_source_directory(self, watcher_fixture):
        assert pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]).exists() == False
        watcher = Watcher(watcher_fixture)
        assert pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]).exists() == True

    def test_watcher_with_a_valid_config_check_desination_directory(self, watcher_fixture):
        assert pathlib.Path(
            watcher_fixture[CONFIG_DESTINATION]).exists() == False
        watcher = Watcher(watcher_fixture)
        assert pathlib.Path(
            watcher_fixture[CONFIG_DESTINATION]).exists() == True

    def test_watcher_initial_state_stopped(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        assert watcher.is_running == False

    def test_watcher_started(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_start_a_running_watcher(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_stopping_a_stopped_watcher(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        watcher.stop()
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped_then_restarted(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_copy_a_single_file_from_source_to_destination(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        (pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]) / "test.txt").touch()
        while watcher.files_processed != 1:
            time.sleep(1)
        watcher.stop()
        assert (pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]) / "test.txt").exists() == False
        assert (pathlib.Path(
            watcher_fixture[CONFIG_DESTINATION]) / "test.txt").exists() == True

    def test_watcher_copy_a_single_file_from_source_to_destination_with_deletesource_false(self, watcher_fixture):
        watcher_fixture[CONFIG_DELETESOURCE
                        ] = False
        watcher = Watcher(watcher_fixture)
        watcher.start()
        (pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]) / "test.txt").touch()
        while watcher.files_processed != 1:
            time.sleep(1)
        watcher.stop()
        assert (pathlib.Path(
            watcher_fixture[CONFIG_SOURCE]) / "test.txt").exists() == True
        assert (pathlib.Path(
            watcher_fixture[CONFIG_DESTINATION]) / "test.txt").exists() == True

    def test_watcher_copy_ten_files_from_source_to_destination(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        for file_number in range(10):
            (pathlib.Path(
                watcher_fixture[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                watcher_fixture[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()

    def test_watcher_copy_fifty_files_from_source_to_destination(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        for file_number in range(50):
            (pathlib.Path(
                watcher_fixture[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                watcher_fixture[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()

    def test_watcher_copy_onehundred_files_from_source_to_destination(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        for file_number in range(100):
            (pathlib.Path(
                watcher_fixture[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                watcher_fixture[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()

    def test_watcher_copy_onethousand_files_from_source_to_destination(self, watcher_fixture):
        watcher = Watcher(watcher_fixture)
        watcher.start()
        for file_number in range(1000):
            (pathlib.Path(
                watcher_fixture[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                watcher_fixture[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()
        
    # Test watcher with invalid confg passed in
