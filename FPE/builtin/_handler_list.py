
from core.handler import IHandler
from copyfile_handler import CopyFileHandler
from sftp_copyfile_handler import SFTPCopyFileHandler

fpe_handler_list: dict[str, IHandler] = {
    "CopyFileHandler": CopyFileHandler, "SFTPCopyFileHandler": SFTPCopyFileHandler}
