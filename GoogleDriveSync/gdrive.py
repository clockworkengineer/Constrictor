"""Class for accessing google drive.

Class to connect, upload, download, maipulate and interrogate files on google drive.
To to this it uses google's own python wrapper Drive API which can be read about at URL
https://developers.google.com/drive/v3/web/quickstart/python.
"""

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
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

   
class GDrive(object):
    """Class for accessing Google Drive.
    
    Open up service to google drive and list/manipulate/upload/download files.
    
    Attrubutes:
    scope:            Google Drive API scope
    secrets_file:     Application secrets file
    credentials_file: Application credentials file
    credentials:      Application credentials
    drive_srvice:     Drive Service
    start_page_token: Saved start page token used to get changes
    """
    
    def __init__(self, scope, secrets_file, credentials_file):
        
        self.scope = scope
        self.secrets_file = secrets_file
        self.credentials_file = credentials_file
        self.credentials = None
        self.drive_service = None
        self.start_page_token = None
        
    def authorize(self, reset_credentials=False):
        """Authorize Application to connect to Google API."""
        
        try :
            
            store = file.Storage(self.credentials_file)
            self.credentials = store.get()
            if not self.credentials or self.credentials.invalid or reset_credentials:
                flow = client.flow_from_clientsecrets(self.secrets_file, self.scope)
                self.credentials = tools.run_flow(flow, store)
        except Exception as e:
            logging.error(e)
        
    def start_service(self):
        """Build service for drive API."""
        
        try :
            
            self.drive_service = build('drive', 'v3',
                                       http=self.credentials.authorize(Http()),
                                       cache_discovery=False)
        except Exception as e:
            logging.error(e)

    def file_list(self, query='', max_files=100, file_fields='name, id'):
        """Return list of file metadata for query pasted in."""
        
        try:       
            
            files_returned = []
            more_files_to_list = True
            next_page_token = None
            
            list_fields = 'nextPageToken, incompleteSearch, files({})'.format(file_fields)
            while more_files_to_list:
                
                list_results = self.drive_service.files().list(pageSize=max_files,
                                                          q=query,
                                                          pageToken=next_page_token,
                                                          fields=list_fields).execute()
            
                items = list_results.get('files', [])
                next_page_token = list_results.get('nextPageToken', None)
                
                if items:  
                    files_returned += items
                    
                if next_page_token == None:
                    more_files_to_list = False
                
        except Exception as e:
            logging.error(e)
         
        finally:
            return (files_returned)
        
    def file_upload(self, local_file, parent_id=None):
        """Upload local file to google drive returning its file id."""
        
        try:
            
            result = None
            
            file_metadata = {'name': os.path.basename(local_file)}
            
            if parent_id:
                file_metadata['parents'] = [ parent_id ]
        
            file_mime_type = magic.from_file(local_file, mime=True)
            
            media = MediaFileUpload(local_file,
                                mimetype=file_mime_type)
            
            result = self.drive_service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        except Exception as e:
            logging.error(e)
        
        finally:                       
            return(result)

    def folder_create(self, folder_name, parent_id=None):
        """Create a folder on google drive"""
        
        try:
            
            result = None
            
            file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
            }
    
            if parent_id:
                file_metadata['parents'] = [ parent_id ]
    
            folder_data = self.drive_service.files().create(body=file_metadata,
                                                            fields='id').execute()
                                                            
            result = folder_data['id']

        except Exception as e:
            logging.error(e)
        
        finally:                       
            return(result)                                           

    def file_get_metadata(self, file_id, file_fields='name, id'):
        """Return metadata associated with google drivefile."""
        
        try:
            
            result = self.drive_service.files().get(fileId=file_id, fields=file_fields).execute()
        
        except Exception as e:
            logging.error(e)
            
        return(result)
    
    def file_download(self, file_id, local_file, mime_type=None):
        """Download/Export google drive file with id to local file system."""
        
        try:
            
            # If mime type set then exporting google applciation file so export (convert)
            
            if mime_type:
                request = self.drive_service.files().export_media(fileId=file_id, mimeType=mime_type[0])
                
            # None google file so just download
            
            else:
                request = self.drive_service.files().get_media(fileId=file_id)
                       
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            while not done:
                done = downloader.next_chunk()
                
            with io.open(local_file, 'wb') as f:
                file_handle.seek(0)
                f.write(file_handle.read())
         
            logging.info('Downloaded file {} to {}'.format(file_id, local_file))
        
        except Exception as e:
            logging.error(e)

    def retrieve_all_changes(self):
        """Retrieve list of changes to google drive since last call"""
    
        try:
            
            changes = []
            
            if not self.start_page_token:
                response = self.drive_service.changes().getStartPageToken().execute()
                self.start_page_token = response.get('startPageToken')
            
            page_token = self.start_page_token
            
            while page_token is not None:
                
                response = self.drive_service.changes().list(pageToken=page_token,
                                                    spaces='drive').execute()
                                                    
                for change in response.get('changes'):
                    changes.append(change)
                 
                if 'newStartPageToken' in response:
                    self.start_page_token = response.get('newStartPageToken')
                 
                page_token = response.get('nextPageToken')
            
        except Exception as e:
            logging.error(e)
            
        return(changes)

