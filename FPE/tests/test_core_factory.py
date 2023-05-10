import pytest

from tests.common import json_file_source
from core.arguments import Arguments
from core.config import Config
from core.factory import Factory, FactoryError
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler


@pytest.fixture()
def reset_factory():
    Factory.clear()
    yield


class TestCoreFactory:

    def test_factory_that_has_noregistered_handlers(self, reset_factory):
        config = Config(Arguments(
            [json_file_source("test_valid.json")])).get_config()
        with pytest.raises(FactoryError):
            _ = Factory.create(config["watchers"][0])

    def test_factory_register_handler(self, reset_factory):
        Factory.register("CopyFile", CopyFileHandler)
        assert "CopyFile" in Factory.handler_function_list()

    def test_factory_unregister_handler(self, reset_factory):
        Factory.register("CopyFile", CopyFileHandler)
        Factory.unregister("CopyFile")
        assert "CopyFile" not in Factory.handler_function_list()
        
    def test_factory_register_an_already_regiestered_handler(self, reset_factory):
        Factory.register("CopyFile", CopyFileHandler)
        Factory.register("CopyFile", CopyFileHandler)
        assert Factory.handler_function_list().count("CopyFile") == 1

    def test_factory_register_a_nonexistant_handler(self, reset_factory):
        with pytest.raises(FactoryError):
            Factory.register("HandlerOne", None)

    def test_factory_register_a_handler_with_no_type(self, reset_factory):
        with pytest.raises(FactoryError):
            Factory.register("", CopyFileHandler)

    def test_factory_unregister_a_nonexistant_handler(self, reset_factory):
        with pytest.raises(FactoryError):
            Factory.unregister("HandlerOne")

    def test_factory_register_more_than_one_handler(self, reset_factory):
        Factory.register("CopyFile", CopyFileHandler)
        Factory.register("SFTPCopyFile", SFTPCopyFileHandler)
        assert "CopyFile" in Factory.handler_function_list()
        assert "SFTPCopyFile" in Factory.handler_function_list()
        assert len(Factory.handler_function_list()) == 2

    def test_factory_create_with_a_handler_that_is_not_registered(self, reset_factory):
        Factory.register("CopyFile", CopyFileHandler)
        Factory.register("SFTPCopyFile", SFTPCopyFileHandler)
        config = Config(Arguments(
            [json_file_source("test_googledrive_handler.json")])).get_config()
        with pytest.raises(FactoryError):
            _ = Factory.create(config["watchers"][0])

    def test_factory_create_with_a_registered_handler(self, reset_factory):
        Factory.register("CopyFile", CopyFileHandler)
        Factory.register("SFTPCopyFile", SFTPCopyFileHandler)
        config = Config(Arguments(
            [json_file_source("test_valid.json")])).get_config()
        assert Factory.create(config["watchers"][0]) != None
