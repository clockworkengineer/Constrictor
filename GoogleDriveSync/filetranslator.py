"""Class for performing file mime type and extension translation for upload/download.

Perform any file extension / mime type mapping between the local and remote drives. The two translation
tables are loaded from a json file but if an error occurs suitable default built-in tables are used.

"""

import logging
import json

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class FileTranslator(object):

    def __init__(self, translator_json_file):

        try:

            # Try to read translator json file

            with open(translator_json_file, 'r') as json_file:
                translator = json.load(json_file)
                self._download_table = dict(translator['downloads'])
                self._upload_table = dict(translator['uploads'])
                logging.info("Translator data read from file {}.".format(translator_json_file))

        except Exception:

            # Fallback on built-in tables

            logging.warning("Translator file {} not found defaulting to built-in.".format(translator_json_file))

            # Indexed by remote mime type. Entry[0] = local file extension, entry[1] = local file mime type

            self._download_table = {
                'application/vnd.google-apps.document':
                    ['docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
                'application/vnd.google-apps.spreadsheet':
                    ['ods', 'application/vnd.oasis.opendocument.spreadsheet'],
                'application/vnd.google-apps.presentation':
                    ['odp', 'application/vnd.oasis.opendocument.presentation']
            }

            # Indexed by local file extenson. Entry[0] = local mime type, entry[1] = remote mime type

            self._upload_table = {
                'csv':
                    ['text/csv', 'application/vnd.google-apps.spreadsheet']
            }

        # Add download table to upload

        for mime_type, file_mapping in self._download_table.items():
            self._upload_table[file_mapping[0]] = [file_mapping[1], mime_type]

        logging.debug('Download Translator Table: {}'.format(self._download_table))
        logging.debug('Upload Translator Table: {}'.format(self._upload_table))

    def remote_mime_type_mapped(self, mime_type):
        """Remote file mime type has a local mapping."""
        return mime_type in self._download_table

    def get_local_file_extension(self, mime_type):
        """Return file extension mapping for remote file."""
        return self._download_table[mime_type][0]

    def get_local_mime_type(self, mime_type):
        """Return mime type mapping for remote file."""
        return self._download_table[mime_type][1]

    def local_file_extension_mapped(self, file_extension):
        """Local file extension has a remote mapping."""
        return file_extension in self._upload_table

    def get_remote_mime_types(self, file_extension):
        """Return remote mime type translation tuple (local mime, remote mime)."""
        return self._upload_table[file_extension]
