"""Class for performing file mime type and extension translation for upload/download.

    Perform any file extension / mime type mapping between the local and remote files.

    TODO:
    1) Make  configurable instead of hard encoded.

"""

import logging

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class FileTranslate(object):

    def __init__(self):
        self._export_table = {
            'application/vnd.google-apps.document':
                ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx'),
            'application/vnd.google-apps.spreadsheet':
                ('application/vnd.oasis.opendocument.spreadsheet', 'ods'),
            'application/vnd.google-apps.presentation':
                ('application/vnd.oasis.opendocument.presentation', 'odp')
        }

    def file_mappable(self, mime_type):
        return (mime_type in self._export_table)

    def get_extension(self, mime_type):
        return (self._export_table[mime_type][1])

    def get_mime_type(self, mime_type):
        return (self._export_table[mime_type][0])
