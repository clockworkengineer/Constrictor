# Make sure handler directory is on sys.path

# import sys
# import os
#
# if os.path.join(os.getcwd(), 'builtin_handlers') not in sys.path:
#     sys.path.insert(1, os.path.join(os.getcwd(), 'builtin_handlers'))

from builtin_handlers.CopyFile import CopyFile
from builtin_handlers.CSVFileToMySQL import CSVFileToMySQL
from builtin_handlers.CSVFileToSQLite import CSVFileToSQLite
from builtin_handlers.SFTPCopyFile import SFTPCopyFile
