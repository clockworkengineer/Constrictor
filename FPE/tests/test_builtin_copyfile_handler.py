import pytest

from core.handler import Handler
from builtin.copyfile_handler import CopyFileHandler, CopyFileHandlerError


class TestBuiltinCopyFileHandler:
    pass
    # Test CopyFileHandler checks for None passed in as config
    # Test CopyFileHandler creates non-existant source
    # Test CopyFileHandler create non-existant destination
    # Test CopyFileHandler single file copied into source then copied to destination
    # Test CopyFileHandler single file copied into source then copied to destination and source file deleted
    # Test CopyFileHandler a whole directory structure copied into source then copied to destination
    # Test CopyFileHandler copies a whole directory structure copied into source then copied to destination amd source files deleted
     
