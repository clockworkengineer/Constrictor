import pytest

from core.factory import Factory
from core.plugin import PluginLoader, PluginLoaderError


@pytest.fixture()
def reset_factory():
    Factory.handler_creation_funcs.clear()
    yield


class TestCorePlugin:

    def test_plugin_load_with_none(self, reset_factory):
        with pytest.raises(PluginLoaderError):
            _ = PluginLoader.load(None)

    def test_plugin_load_with_an_empty_list(self, reset_factory):
        with pytest.raises(PluginLoaderError):
            _ = PluginLoader.load([])

    def test_plugin_load_with_non_existant_handler_type(self, reset_factory):
        with pytest.raises(PluginLoaderError):
            _ = PluginLoader.load(["plugins.test_handler"])

    def test_plugin_load_with_valid_handler_type(self, reset_factory):
        PluginLoader.load(["plugins.fileannouncer_handler"])
        assert len(Factory.handler_creation_funcs) == 1
        assert "FileAnnouncer" in Factory.handler_creation_funcs.keys()
