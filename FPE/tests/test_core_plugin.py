"""TEST"""
# pylint: disable=missing-function-docstring, missing-class-docstring

import pytest

from core.factory import Factory
from core.plugin import PluginLoader, PluginLoaderError


@pytest.fixture(name="reset_factory")
def fixture_reset_factory() -> None:
    Factory.clear()
    yield


class TestCorePlugin:
    def test_plugin_load_with_none(self, reset_factory) -> None:
        with pytest.raises(PluginLoaderError):
            PluginLoader.load(None)  # type: ignore

    def test_plugin_load_with_an_empty_list(self, reset_factory) -> None:
        with pytest.raises(PluginLoaderError):
            PluginLoader.load([])

    def test_plugin_load_with_non_existant_handler_type(self, reset_factory) -> None:
        with pytest.raises(PluginLoaderError):
            PluginLoader.load(["plugins.test_handler"])

    def test_plugin_load_with_valid_handler_type(self, reset_factory) -> None:
        PluginLoader.load(["plugins.fileannouncer_handler"])
        assert len(Factory.handler_function_list()) == 1
        assert "FileAnnouncer" in Factory.handler_function_list()
