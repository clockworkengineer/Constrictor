from pytest import raises
import os

from core.arguments import Arguments
from core.config import Config, ConfigError


class TestConfig:
    
    def test_config_with_valid_json_file(self):
        config = Config(Arguments([os.path.join(os.getcwd(), "FPE","tests","test.json")])).get_config()
        assert config["plugins"][0] == "plugins.fileannouncer_handler"
        
    def test_config_with_invalid_json_file(self):
        with raises(ConfigError):
            config = Config(Arguments([os.path.join(os.getcwd(), "FPE","tests","test_invalid.json")]))
        