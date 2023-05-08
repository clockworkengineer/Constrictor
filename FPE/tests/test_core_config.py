import pytest
import pathlib

from core.arguments import Arguments
from core.config import Config, ConfigError

@pytest.fixture()
def json_file_source():
    yield pathlib.Path.cwd() / "FPE" / "tests" / "json"
    
class TestCoreConfig:

    def test_config_with_valid_json_file(self,json_file_source):
        config = Config(Arguments(
            [str(json_file_source / "test_valid.json")])).get_config()
        assert config["plugins"][0] == "plugins.fileannouncer_handler"
        assert config["watchers"][0]["type"] == "CopyFile"

    def test_config_with_invalid_json_file(self,json_file_source):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [str(json_file_source / "test_invalid.json")]))

    def test_config_with_no_plugin_key(self,json_file_source):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [str(json_file_source / "test_noplugin_key.json")]))
            config.validate()

    def test_config_with_no_watchers_key(self,json_file_source):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [str(json_file_source / "test_nowatchers_key.json")]))
            config.validate()

    def test_config_with_watcher_source_missing(self,json_file_source):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [str(json_file_source / "test_watcher_source_missing.json")]))
            config.validate()

    def test_config_with_watcher_name_missing(self,json_file_source):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [str(json_file_source / "test_watcher_name_missing.json")]))
            config.validate()

    def test_config_with_watcher_type_missing(self,json_file_source):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [str(json_file_source / "test_watcher_type_missing.json")]))
            config.validate()
