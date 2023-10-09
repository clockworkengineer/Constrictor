"""TEST"""
# pylint: disable=missing-function-docstring, missing-class-docstring, unused-argument

import pytest

from tests.common import json_file_source

from core.arguments import Arguments
from core.config import Config
from core.engine import Engine, EngineError


class TestCoreEngine:
    # Test pass None as engine config

    def test_core_engine_pass_none_as_engine_config(self) -> None:
        with pytest.raises(EngineError):
            _: Engine = Engine(None)  # type: ignore

    # Test valid engine config loads ok

    def test_core_engine_with_valid_config_file(self) -> None:
        engine_config = Config(
            Arguments([json_file_source("test_valid.json")])
        ).get_config()
        engine: Engine = Engine(engine_config)
        assert engine is not None
        assert engine.is_running is False

    def test_core_engine_with_valid_config_file_startsup(self) -> None:
        engine_config = Config(
            Arguments([json_file_source("test_valid.json")])
        ).get_config()
        engine: Engine = Engine(engine_config)
        engine.startup()
        assert engine.is_running


# Test no handlers in config works ok
# Test empty plugins works ok
# Test to create a watcher
# Test to delete a watcher
# Test to start a watcher
# Test to stop a watcher
# Test to start non-existant watcher
# Test to stop non-existant watcher
