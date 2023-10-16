"""TEST"""
# pylint: disable=missing-function-docstring, missing-class-docstring, unused-argument

import pytest

from tests.common import json_file_source

from core.constants import CONFIG_WATCHERS, CONFIG_PLUGINS, CONFIG_NAME
from core.arguments import Arguments
from core.config import Config
from core.consumer import ConsumerError
from core.engine import Engine, EngineError
from core.factory import FactoryError
from core.plugin import PluginLoaderError


def failure_callback(watcher_name: str) -> None:
    pass


def create_engine(config_file: str) -> Engine:
    engine_config = Config(Arguments([json_file_source(config_file)])).get_config()
    return Engine(engine_config)


class TestCoreEngine:
    def test_core_engine_pass_none_as_engine_config(self) -> None:
        with pytest.raises(EngineError):
            _: Engine = Engine(None)  # type: ignore

    def test_core_engine_with_valid_config_file(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        assert engine is not None
        assert engine.is_running is False

    def test_core_engine_with_valid_config_file_startup_with_no_failure_callback(
        self,
    ) -> None:
        engine: Engine = create_engine("test_valid.json")
        with pytest.raises(ConsumerError):
            engine.startup()

    def test_core_engine_with_valid_config_file_startup_with_failure_callback(
        self,
    ) -> None:
        engine: Engine = create_engine("test_valid.json")
        engine.set_failure_callback(failure_callback)
        engine.startup()
        assert engine.is_running

    def test_core_engine_with_no_watchers_in_config(self) -> None:
        engine_config = Config(
            Arguments([json_file_source("test_valid.json")])
        ).get_config()
        engine_config[CONFIG_WATCHERS] = []
        engine: Engine = Engine(engine_config)
        assert engine is not None

    def test_core_engine_with_no_plugins_in_config(self) -> None:
        engine_config = Config(
            Arguments([json_file_source("test_valid.json")])
        ).get_config()
        engine_config[CONFIG_PLUGINS] = []
        with pytest.raises(PluginLoaderError):
            _: Engine = Engine(engine_config)

    def test_core_engine_create_a_watcher(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        assert len(engine.watchers_list) == 0
        engine.create_watcher(watcher_config)
        assert len(engine.watchers_list) == 1

    def test_core_engine_delete_a_watcher(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        engine.create_watcher(watcher_config)
        assert len(engine.watchers_list) == 1
        engine.delete_watcher(watcher_config[CONFIG_NAME])
        assert len(engine.watchers_list) == 0

    def test_core_engine_create_a_watcher_with_invalid_type(self) -> None:
        engine: Engine = create_engine("test_invalid_watcher_type.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        with pytest.raises(FactoryError):
            engine.create_watcher(watcher_config)
        assert len(engine.watchers_list) == 0

    def test_core_engine_delete_a_non_existant_watcher(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        engine.create_watcher(watcher_config)
        assert len(engine.watchers_list) == 1
        with pytest.raises(EngineError):
            engine.delete_watcher("Not there")
        assert len(engine.watchers_list) == 1

    def test_core_engine_create_and_start_a_watcher(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        engine.create_watcher(watcher_config)
        engine.start_watcher(watcher_config[CONFIG_NAME])
        assert engine.is_watcher_running(watcher_config[CONFIG_NAME])

    def test_core_engine_create_and_start_a_watcher_then_stop(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        engine.create_watcher(watcher_config)
        engine.start_watcher(watcher_config[CONFIG_NAME])
        engine.stop_watcher(watcher_config[CONFIG_NAME])
        assert engine.is_watcher_running(watcher_config[CONFIG_NAME]) is False

    def test_core_engine_start_noexistant_watcher(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        engine.create_watcher(watcher_config)
        with pytest.raises(EngineError):
            engine.start_watcher("Not There")

    def test_core_engine_stop_noexistant_watcher(self) -> None:
        engine: Engine = create_engine("test_valid.json")
        watcher_config = engine.running_config[CONFIG_WATCHERS][0]
        engine.set_failure_callback(failure_callback)
        engine.create_watcher(watcher_config)
        engine.start_watcher(watcher_config[CONFIG_NAME])
        with pytest.raises(EngineError):
            engine.stop_watcher("Not There")
