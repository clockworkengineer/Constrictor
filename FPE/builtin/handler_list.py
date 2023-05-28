"""FPE builtin handler table.
"""

from typing import Callable

from core.interface.ihandler import IHandler
from builtin.copyfile_handler import CopyFileHandler
from builtin.sftp_copyfile_handler import SFTPCopyFileHandler

fpe_handler_list: dict[str, Callable[..., IHandler]] = {
    "CopyFile": CopyFileHandler, "SFTPCopyFile": SFTPCopyFileHandler}
