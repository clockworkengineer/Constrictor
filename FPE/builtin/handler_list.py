"""FPE built-in handler table.
"""

from typing import Callable

from core.interface.ihandler import IHandler
from builtin.copyfile_handler import CopyFileHandler
from builtin.ftp_copyfile_handler import FTPCopyFileHandler
from builtin.csvfile_to_sqlite_handler import CSVFileToSQLiteHandler

fpe_handler_list: dict[str, Callable[..., IHandler]] = {
    "CopyFile": CopyFileHandler, "FTPCopyFile": FTPCopyFileHandler, "CSVFileToSQLite": CSVFileToSQLiteHandler}
