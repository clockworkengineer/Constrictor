"""Class for accessing remote drive.

This is a child class of GDevice that caches the remote  Google drive contents
for performance and reduce the number of http requests. It also creates an uploader
object if it is specified so that local files can bu uploaded to the remote drive.
"""

from gdrive import GDrive, GDriveError
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class _RemoteUploader(FileSystemEventHandler):
    """Private class to upload watched folder files to Google drive.

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

            # Create observer and start watching folder

            self._observer = Observer()
            self._observer.schedule(self, self._local_upload_path, recursive=False)
            self._observer.start()

        except (Exception, GDriveError) as e:
            logging.error(e)
            raise e

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

        except (Exception, GDriveError) as e:
            logging.error(e)
            raise e


class RemoteDrive(GDrive):
    """Class to access remote drive.
    
    Access remote drive files (keeping a complete file cache locally). The force_refresh parameter
    is used to force a remote file cache update and not rely on the changes API as these can take
    minutes to filter back and is used when more immediate local updates are required.
    
    Attrubutes:
        _file_translator   File translator
        _forece_refresh    == True then refresh file cache oneach has_chaneged().
        file_cache:        Drive file cache.
        root_folder_id:    File ID for root folder.
    """

    def __init__(self, credentials, local_upload_path, file_translator, force_refresh=False):

        try:

            super().__init__(credentials)

            self._file_translator = file_translator
            self._force_refresh = force_refresh
            self.root_folder_id = self.file_get_metadata('root').get('id', None)

            self._refresh_file_cache()

            # Create file uploader object

            if local_upload_path:
                self._uploader = _RemoteUploader(credentials, local_upload_path, file_translator)
                logging.info("Created upload folder {} for Google Drive.".format(local_upload_path))

            logging.debug('Remote Drive force refresh = {}.'.format(self._force_refresh))

        except (Exception, GDriveError) as e:
            logging.error(e)
            raise e

    def _refresh_file_cache(self, cache_changes=None):
        """Refresh remote drive file cache."""

        try:

            if cache_changes is None:
                cache_changes = []

            # Complete refresh

            if not cache_changes:
                self.file_cache = self.file_list(query='not trashed',
                                                 file_fields=
                                                 'name, id, parents, size, mimeType, modifiedTime, trashed')

            # Updadte from passed in changes

            else:
                for change in cache_changes:
                    for index in range(len(self.file_cache)):
                        if self.file_cache[index]['id'] == change['id']:
                            if not change['trashed']:
                                self.file_cache[index] = change
                                logging.debug('Replacing remote file cache entry {}'.format(change['id']))
                            else:
                                del (self.file_cache[index])
                                logging.debug('Deleting file cache entry {}'.format(change['id']))
                            break
                    else:
                        self.file_cache.append(change)
                        logging.debug('Adding file cache entry {}'.format(change['id']))

        except (Exception, GDriveError) as e:
            logging.error(e)
            raise e

    def _build_changes(self, drive_changes):
        """Build changes list compatible with file cache entry"""

        changes = []

        for change_data in drive_changes:
            if not change_data['removed']:
                file_data = self.file_get_metadata(change_data['fileId'],
                                                   file_fields=
                                                   'name, id, parents, size, mimeType, modifiedTime, trashed')
                changes.append(file_data)

        return (changes)

    def has_changed(self):
        """Has remote drive changed."""

        try:

            drive_changes = self.retrieve_all_changes()

            if self._force_refresh or len(drive_changes) > 0:
                self._refresh_file_cache(self._build_changes(drive_changes))

        except (Exception, GDriveError) as e:
            logging.error(e)
            raise e

        return self._force_refresh or (len(drive_changes) > 0)

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
