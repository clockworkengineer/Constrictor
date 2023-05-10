from typing import Any

from copyfile_handler import CopyFileHandler
from sftp_copyfile_handler import SFTPCopyFileHandler

handler_list: dict[str, Any] = {
    "CopyFileHandler": CopyFileHandler, "SFTPCopyFileHandler": SFTPCopyFileHandler}
