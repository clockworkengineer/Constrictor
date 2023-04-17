from pytest import raises
import os

from core.arguments import Arguments
from core.config import Config
from core.factory import Factory, FactoryError
from builtin.copyfile_handler import CopyFileHandler


class TestFactory:

    # Test empty factory
    def test_factory_that_has_noregistered_handlers(self):

        config = Config(Arguments([os.path.join(
            os.getcwd(), "FPE", "tests", "json", "test_valid.json")])).get_config()

        with raises(FactoryError):
            _ = Factory.create(config["watchers"][0])

    # Test register handler

    def test_factory_register_handler(self):

        Factory.register("CopyFile", CopyFileHandler)
        assert "CopyFile" in Factory.handler_creation_funcs.keys()

    # Test unregister handler

    def test_factory_unregister_handler(self):

        Factory.register("CopyFile", CopyFileHandler)
        Factory.unregister("CopyFile")
        assert "CopyFile" not in Factory.handler_creation_funcs.keys()

    # Test register non existant handler
    def test_factory_register_a_nonexistant_handler(self):
        with raises(FactoryError):
            Factory.register("HandlerOne", None)

    def test_factory_register_a_handler_with_no_type(self):
        with raises(FactoryError):
            Factory.register("", CopyFileHandler)

    # Test unregister non existant handler
    # Test register more than one handler
    # Test try to create non-existant handler (unregistered)
    # Test try to create a a registered handler
