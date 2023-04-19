import pytest
import os

from core.arguments import Arguments
from core.config import Config, ConfigError


class TestCoreConfig:

    def test_config_with_valid_json_file(self):
        config = Config(Arguments(
            [os.path.join(os.getcwd(), "FPE", "tests", "json", "test_valid.json")])).get_config()
        assert config["plugins"][0] == "plugins.fileannouncer_handler"
        assert config["watchers"][0]["type"] == "CopyFile"

    def test_config_with_invalid_json_file(self):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [os.path.join(os.getcwd(), "FPE", "tests", "json", "test_invalid.json")]))

    def test_config_with_no_plugin_key(self):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [os.path.join(os.getcwd(), "FPE", "tests", "json", "test_noplugin_key.json")]))
            config.validate()

    def test_config_with_no_watchers_key(self):
        with pytest.raises(ConfigError):
            config = Config(Arguments(
                [os.path.join(os.getcwd(), "FPE", "tests", "json", "test_nowatchers_key.json")]))
            config.validate()

    def test_config_with_watcher_source_missing(self):
        with pytest.raises(ConfigError):
            config = Config(Arguments([os.path.join(
                os.getcwd(), "FPE", "tests", "json", "test_watcher_source_missing.json")]))
            config.validate()

    def test_config_with_watcher_name_missing(self):
        with pytest.raises(ConfigError):
            config = Config(Arguments([os.path.join(
                os.getcwd(), "FPE", "tests", "json", "test_watcher_name_missing.json")]))
            config.validate()

    def test_config_with_watcher_type_missing(self):
        with pytest.raises(ConfigError):
            config = Config(Arguments([os.path.join(
                os.getcwd(), "FPE", "tests", "json", "test_watcher_type_missing.json")]))
            config.validate()
