import pytest
import os
import time
from typing import Any

from core.arguments import Arguments
from core.config import Config
from core.watcher import Watcher, WatcherError
from core.factory import Factory
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler


@pytest.fixture()
def reset_factory_and_return_config() -> dict[str, Any]:
    
    Factory.handler_creation_funcs.clear()
    Factory.register("CopyFile", CopyFileHandler)
    Factory.register("SFTPCopyFile", SFTPCopyFileHandler)

    config = Config(Arguments(
        [os.path.join(os.getcwd(), "FPE", "tests", "json", "test_valid.json")])).get_config()
    
    yield config["watchers"][0]


class TestCoreWatcher:

    def test_watcher_with_config_of_none(self, reset_factory_and_return_config):
        
        with pytest.raises(WatcherError):
            _ = Watcher(None)

    def test_watcher_with_a_valid_config(self, reset_factory_and_return_config):

        watcher = Watcher(reset_factory_and_return_config)

        assert watcher != None

    def test_watcher_initial_state_stopped(self, reset_factory_and_return_config):

        watcher = Watcher(reset_factory_and_return_config)

        assert watcher.started == False

    def test_watcher_started(self, reset_factory_and_return_config):

        watcher = Watcher(reset_factory_and_return_config)

        watcher.start()

        assert watcher.started == True

    def test_watcher_started_then_stopped(self, reset_factory_and_return_config):

        watcher = Watcher(reset_factory_and_return_config)

        watcher.start()
        time.sleep(1)
        watcher.stop()

        assert watcher.started == False

    # Test watcher with invalid confg passed in
