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


class FileTranslator(object):

    def __init__(self):

        self._download_table = {
            'application/vnd.google-apps.document':
                ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx'),
            'application/vnd.google-apps.spreadsheet':
                ('application/vnd.oasis.opendocument.spreadsheet', 'ods'),
            'application/vnd.google-apps.presentation':
                ('application/vnd.oasis.opendocument.presentation', 'odp')
        }

        self._upload_table = {
            'csv':
                ('text/csv', 'application/vnd.google-apps.spreadsheet',)
        }

        for mime_type, file_mapping in self._download_table.items():
            self._upload_table[file_mapping[1]] = (file_mapping[0], mime_type)

    def remote_mime_type_mapped(self, mime_type):
        return (mime_type in self._download_table)

    def get_local_file_extension(self, mime_type):
        return (self._download_table[mime_type][1])

    def get_local_mime_type(self, mime_type):
        return (self._download_table[mime_type][0])

    def local_file_extension_mapped(self, file_extension):
        return (file_extension in self._upload_table)

    def get_remote_mime_types(self, file_extension):
        return (self._upload_table[file_extension])
