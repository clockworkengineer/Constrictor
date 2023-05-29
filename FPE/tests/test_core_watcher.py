import pytest
import time

from tests.common import json_file_source
from core.constants import CONFIG_WATCHERS
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


class TestCoreWatcher:

    def test_watcher_with_config_of_none(self):
        with pytest.raises(WatcherError):
            _ = Watcher(None)

    def test_watcher_with_a_valid_config(self, reset_factory_and_return_config):
        watcher = Watcher(reset_factory_and_return_config)
        assert watcher != None

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
    # Test watcher copying file with deletesource set to false.
    # Test watcher copyinh file with deletesource set to true
    # Test watcher with invalid confg passed in
