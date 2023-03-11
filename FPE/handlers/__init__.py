# Make sure handler directory is on sys.path

# import sys
# import os
#
# if os.path.join(os.getcwd(), 'handlers') not in sys.path:
#     sys.path.insert(1, os.path.join(os.getcwd(), 'handlers'))

from handlers.CopyFile import CopyFile
# from handlers.CSVFileToMySQL import CSVFileToMySQL
# from handlers.CSVFileToSQLite import CSVFileToSQLite
# from handlers.SFTPCopyFile import SFTPCopyFile
