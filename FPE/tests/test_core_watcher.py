import pytest
import time
import pathlib
import shutil

from tests.common import json_file_source
from core.constants import CONFIG_WATCHERS, CONFIG_SOURCE, CONFIG_DESTINATION
from core.arguments import Arguments
from core.config import Config, ConfigDict
from core.watcher import Watcher, WatcherError
from core.factory import Factory
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler


@pytest.fixture()
def reset_factory_and_return_config() -> ConfigDict:
    Factory.clear()
    Factory.register("CopyFile", CopyFileHandler)
    Factory.register("SFTPCopyFile", SFTPCopyFileHandler)
    config = Config(Arguments(
        [json_file_source("test_valid.json")])).get_config()
    yield config[CONFIG_WATCHERS][0]
    shutil.rmtree(config[CONFIG_WATCHERS][0][CONFIG_SOURCE])
    shutil.rmtree(config[CONFIG_WATCHERS][0][CONFIG_DESTINATION])


class TestCoreWatcher:

    def test_watcher_with_config_of_none(self):
        with pytest.raises(WatcherError):
            _ = Watcher(None)

    def test_watcher_with_a_valid_config(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        assert watcher != None

    def test_watcher_with_a_valid_config_check_source_directory(self, reset_factory_and_return_config):
        assert pathlib.Path(
            reset_factory_and_return_config[CONFIG_SOURCE]).exists() == False
        watcher = Watcher(reset_factory_and_return_config)
        assert pathlib.Path(
            reset_factory_and_return_config[CONFIG_SOURCE]).exists() == True

    def test_watcher_with_a_valid_config_check_desination_directory(self, reset_factory_and_return_config):
        assert pathlib.Path(
            reset_factory_and_return_config[CONFIG_DESTINATION]).exists() == False
        watcher = Watcher(reset_factory_and_return_config)
        assert pathlib.Path(
            reset_factory_and_return_config[CONFIG_DESTINATION]).exists() == True

    def test_watcher_initial_state_stopped(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        assert watcher.is_running == False

    def test_watcher_started(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_start_a_running_watcher(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_stopping_a_stopped_watcher(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        watcher.stop()
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        assert watcher.is_running == False

    def test_watcher_started_then_stopped_then_restarted(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        time.sleep(1)
        watcher.stop()
        watcher.start()
        assert watcher.is_running == True

    def test_watcher_copy_a_single_file_from_source_to_destination(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        (pathlib.Path(
            reset_factory_and_return_config[CONFIG_SOURCE]) / "test.txt").touch()
        while watcher.files_processed != 1:
            time.sleep(1)
        watcher.stop()
        assert (pathlib.Path(
            reset_factory_and_return_config[CONFIG_DESTINATION]) / "test.txt").exists() == True
        
    def test_watcher_copy_ten_files_from_source_to_destination(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        for file_number in range(10):
            (pathlib.Path(
                reset_factory_and_return_config[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                reset_factory_and_return_config[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()
        
    def test_watcher_copy_fifty_files_from_source_to_destination(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        for file_number in range(50):
            (pathlib.Path(
                reset_factory_and_return_config[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                reset_factory_and_return_config[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()
        
    def test_watcher_copy_onehundred_files_from_source_to_destination(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        for file_number in range(100):
            (pathlib.Path(
                reset_factory_and_return_config[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                reset_factory_and_return_config[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()
        
    def test_watcher_copy_onethousand_files_from_source_to_destination(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        watcher.start()
        for file_number in range(1000):
            (pathlib.Path(
                reset_factory_and_return_config[CONFIG_SOURCE]) / f"test{file_number}.txt").touch()
            while watcher.files_processed != (file_number+1):
                time.sleep(0.01)
            assert (pathlib.Path(
                reset_factory_and_return_config[CONFIG_DESTINATION]) / f"test{file_number}.txt").exists() == True
        watcher.stop()
    # Test watcher copying file with deletesource set to false.
    # Test watcher copying file with deletesource set to true
    # Test watcher with invalid confg passed in
