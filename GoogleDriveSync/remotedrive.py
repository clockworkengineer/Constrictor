"""Class for accessing remote drive.

This is a child class of GDevice that caches the remote  Google drive contents
for performance and reduce the number of http requests,
"""

from gdrive import GDrive
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from googleapiclient.errors import HttpError

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class _RemoteUploader(FileSystemEventHandler):
    """Class to upload watched folder files to Google drive.

    Child class of FileSystemEventHandle that creates its own watchdog observer
    and sets itself as the file handler. Its on_created method is overridden to upload
    any files created to a specific folder on Google drive.

    Attributes:
        _credentials:             Token returned during Google drive authorization
        _local_upload_path:       Local upload folder path
        _remote_upload_folder:    Remote upload folder
        _file_translator          File translator
    """

    def __init__(self, credentials, local_upload_path, file_translator):
        """Set attributes, create file observer and start watching it."""
        try:

            self._credentials = credentials
            self._local_upload_path = local_upload_path
            self._remote_upload_folder = os.path.basename(local_upload_path)
            self._file_translator = file_translator

            if not os.path.exists(local_upload_path):
                os.makedirs(local_upload_path)

            self._drive = GDrive(self._credentials)

            # If remote folder does not exist create it off root

            file_query = "(name = '{}') and (not trashed)".format(self._remote_upload_folder)

            self._upload_folder = self._drive.file_list(query=file_query,
                                                        file_fields=
                                                        'name, id, parents')

            if len(self._upload_folder) == 0:
                self._drive.folder_create(self._remote_upload_folder)
                self._upload_folder = self._drive.file_list(query=file_query,
                                                            file_fields=
                                                            'name, id, parents')

            self._observer = Observer()

            self._observer.schedule(self, self._local_upload_path,
                                    recursive=False)

            self._observer.start()

        except Exception as e:
            logging.error(e)

    def on_created(self, event):
        """Upload file to Google drive."""
        try:

            logging.info("Uploading file '{}' to Google drive folder '{}'.".
                         format(event.src_path, self._remote_upload_folder))

            file_extension = os.path.splitext(event.src_path)[1][1:]

            mime_types = None
            if self._file_translator.local_file_extension_mapped(file_extension):
                mime_types = self._file_translator.get_remote_mime_types(file_extension)

            self._drive.file_upload(event.src_path, self._upload_folder[0]['id'], mime_types)

        except HttpError as e:
            logging.error(e)
            raise e

class RemoteDrive(GDrive):
    """Class to access remote drive.
    
    Access remote drive files (keeping a complete file cache locally).
    
    Attrubutes:
        _file_translator   File translator object
        file_cache:        Drive file cache.
        root_folder_id:    File ID for root folder.
    """

    def __init__(self, credentials, upload_folder, file_translator):
        
        try:
            
            super().__init__(credentials)

            self._file_translator = file_translator

            self.root_folder_id = self.file_get_metadata('root').get('id', None)

            # Create file uploader object

            if upload_folder:
                uploader = _RemoteUploader(credentials, upload_folder, file_translator)
                logging.info("Created upload folder {} for Google drive.".format(upload_folder))

        except Exception as e:
            logging.error(e)
            
    def refresh_file_cache(self):
        """Refresh remote drive file cache."""
        
        try:

            self.file_cache = self.file_list(query='not trashed',
                                             file_fields=
                                             'name, id, parents, mimeType, modifiedTime')

        except Exception as e:
            logging.error(e)
    
    # Properties
     
    @property
    def file_cache(self):
        return self._file_cache
    
    @file_cache.setter
    def file_cache(self, file_cache):
        self._file_cache = file_cache
        
    @property
    def root_folder_id(self):
        return self._root_folder_id
    
    @root_folder_id.setter
    def root_folder_id(self, root_folder_id):
        self._root_folder_id = root_folder_id
