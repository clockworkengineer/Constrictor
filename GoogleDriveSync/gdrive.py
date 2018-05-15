"""Class for accessing google drive.

Class to connect, upload, download, maipulate and interrogate files on Google drive.
To to this it uses google's own python wrapper Drive API which can be read about at URL
https://developers.google.com/drive/v3/web/quickstart/python.
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# noinspection PyUnresolvedReferences
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import os
import io
import magic
import logging

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"

# Switch off INFO google logging

logging.getLogger("googleapiclient").setLevel(logging.WARNING)


class GDriveUploader(FileSystemEventHandler):
    """Class to upload watched folder files to Google drive.
    
    Child class of FileSystemEventHandle that creates its own watchdog observer
    and sets itself as the file handler. Its on_created method is overridden to upload
    any files created to a specific folder on Google drive.
    
    Attributes:
        _credentials:             Token returned during Google drive authorization
        _local_upload_path:       Local upload folder path
        _remote_upload_folder:    Remote upload folder
    """

    def __init__(self, credentials, local_upload_path, remote_upload_folder):
        """Set attributes, create file observer and start watching it."""
        try:

            self._credentials = credentials
            self._local_upload_path = local_upload_path
            self._remote_upload_folder = remote_upload_folder

            if not os.path.exists(local_upload_path):
                os.makedirs(local_upload_path)

            self._drive = GDrive(self._credentials)

            # If remote folder does not exist create it off root

            file_query = "(name = '{}') and (not trashed)".format(remote_upload_folder)

            self._upload_folder = self._drive.file_list(query=file_query,
                                                        file_fields=
                                                        'name, id, parents')

            if len(self._upload_folder) == 0:
                self._drive.folder_create(remote_upload_folder)
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

            self._drive.file_upload(event.src_path, parent_id=self._upload_folder[0]['id'])

        except HttpError as e:
            logging.error(e)
            raise e


def g_authorize(scope, secrets_file, credentials_file, credentials_refresh=False):
    """Function for getting authoization token for use with Google drive.
    
    Get access token from Google using OAuth 2.0.
    
    Args:
        scope:                Google drive API scope
        secrets_file:         Application secrets file
        credentials_file:     Application credentials file
        credentials_refresh:  Refresh credentials
    
    Returns: 
        Credentials(token) for acccessing Google drive.       
    """

    credentials = None

    try:
        store = file.Storage(credentials_file)
        credentials = store.get()
        if not credentials or credentials.invalid or credentials_refresh:
            flow = client.flow_from_clientsecrets(secrets_file, scope)
            credentials = tools.run_flow(flow, store, tools.argparser.parse_args(args=[]))
    except Exception as e:
        logging.error(e)

    return credentials


class GDrive(object):
    """Class for accessing Google Drive.
    
    Open up service to Google drive to list/manipulate/upload/download files.
    
    Attributes:
        credentials:       Application credentials(token) for accessing drive
        _drive_service:     Drive Service
        _start_page_token: Saved start page token used to get changes
    """

    def __init__(self, credentials):

        self.credentials = credentials

        self._start_page_token = None
        self._drive_service = build('drive', 'v3',
                                    http=self._credentials.authorize(Http()),
                                    cache_discovery=False)

    def file_list(self, query='', max_files=100, file_fields='name, id'):
        """Return list of file metadata for query pasted in."""

        try:

            files_returned = []
            more_files_to_list = True
            next_page_token = None

            list_fields = 'nextPageToken, incompleteSearch, files({})'.format(file_fields)
            while more_files_to_list:

                list_results = self._drive_service.files().list(pageSize=max_files,
                                                                q=query,
                                                                pageToken=next_page_token,
                                                                fields=list_fields).execute()

                items = list_results.get('files', [])
                next_page_token = list_results.get('nextPageToken', None)

                if items:
                    files_returned += items

                if next_page_token is None:
                    more_files_to_list = False

        except HttpError as e:
            logging.error(e)
            raise e

        logging.debug('List File (Length={}).Items={}'.format(len(files_returned), files_returned))

        return files_returned

    def folder_create(self, folder_name, parent_id=None):
        """Create a folder on google drive"""

        try:

            result = None

            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder_data = self._drive_service.files().create(body=file_metadata,
                                                             fields='id').execute()

            result = folder_data['id']

        except HttpError as e:
            logging.error(e)
            raise e

        return result

    def file_get_metadata(self, file_id, file_fields='name, id'):
        """Return metadata associated with google drivefile."""

        try:

            result = self._drive_service.files().get(fileId=file_id, fields=file_fields).execute()

        except HttpError as e:
            logging.error(e)
            raise e

        return result

    def file_download(self, file_id, local_file, mime_type=None):
        """Download/Export google drive file with id to local file system."""

        try:

            # If mime type set then exporting google applciation file so export (convert)

            if mime_type:
                request = self._drive_service.files().export_media(fileId=file_id, mimeType=mime_type[0])

            # None google file so just download

            else:
                request = self._drive_service.files().get_media(fileId=file_id)

            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            while not done:
                done = downloader.next_chunk()

            with io.open(local_file, 'wb') as f:
                file_handle.seek(0)
                f.write(file_handle.read())

            logging.info('Downloaded file {} to {}'.format(file_id, local_file))

        except HttpError as e:
            logging.error(e)
            raise e

    def file_upload(self, local_file, parent_id=None, mime_type=None):
        """Upload local file to google drive returning its file id."""

        try:

            result = None

            file_metadata = {'name': os.path.basename(local_file)}

            if mime_type:
                file_metadata['mimeType'] = mime_type

            if parent_id:
                file_metadata['parents'] = [parent_id]

            file_mime_type = magic.from_file(local_file, mime=True)

            media = MediaFileUpload(local_file,
                                    mimetype=file_mime_type,
                                    resumable=True)

            result = self._drive_service.files().create(body=file_metadata,
                                                        media_body=media,
                                                        fields='id').execute(
            )
        except HttpError as e:
            logging.error(e)
            raise e

        return result

    def retrieve_all_changes(self):
        """Retrieve list of changes to google drive since last call"""

        try:

            changes = []

            if not self._start_page_token:
                response = self._drive_service.changes().getStartPageToken().execute()
                self._start_page_token = response.get('startPageToken')

            page_token = self._start_page_token

            while page_token is not None:

                response = self._drive_service.changes().list(pageToken=page_token,
                                                              spaces='drive').execute()

                for change in response.get('changes'):
                    changes.append(change)

                if 'newStartPageToken' in response:
                    self._start_page_token = response.get('newStartPageToken')

                page_token = response.get('nextPageToken')

        except HttpError as e:
            logging.error(e)
            raise e

        return changes

    # Properties

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, credentials):
        self._credentials = credentials
