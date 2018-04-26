from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os, io
import magic


class GDrive(object):
    
    def __init__(self, scope, secrets_file, credentials_file):
        
        self.scope = scope
        self.secrets_file = secrets_file
        self.credentials_file = credentials_file
        self.credentials = None
        self.drive_service = None
        
    def authorize(self, reset_credentials=False):
    
        try :
            store = file.Storage(self.credentials_file)
            self.credentials = store.get()
            if not self.credentials or self.credentials.invalid or reset_credentials:
                flow = client.flow_from_clientsecrets(self.secrets_file, self.scope)
                self.credentials = tools.run_flow(flow, store)
        except Exception as e:
            print(e)
        
    def start_service(self):
        
        try :
            self.drive_service = build('drive', 'v3',
                                       http=self.credentials.authorize(Http()))
        except Exception as e:
            print(e)

    def file_list(self, query='', max_files=100, file_fields='name, id'):
        
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
            print(e)
         
        finally:
            return (files_returned)
        
    def file_upload(self, file_path, parent_id=None):
        
        file_metadata = {'name': os.path.basename(file_path)}
        
        if parent_id:
            file_metadata['parents'] = [ parent_id ]

        file_mime_type = magic.from_file(file_path, mime=True)
        
        media = MediaFileUpload(file_path,
                            mimetype=file_mime_type)
        
        result = self.drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
        
    def file_download(self, file_id, local_file_path):
        
        request = self.drive_service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))

        with io.open(local_file_path, 'wb') as f:
            file_handle.seek(0)
            f.write(file_handle.read())

    def folder_create(self, folder_name):
        
        file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder_data = self.drive_service.files().create(body=file_metadata,
                                                        fields='id').execute()
                                            
        return(folder_data['id'])
    
    def file_get_metadata(self, file_id, file_fields='*'):
        
        data = self.drive_service.files().get(fileId=file_id, fields=file_fields).execute()
        
        return(data)
    
    def file_export(self, file_id, local_file_path, mime_type, file_extension):
        
        request = self.drive_service.files().export_media(fileId=file_id, mimeType=mime_type)

        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))

        fn = '{}.{}'.format(os.path.splitext(local_file_path)[0], file_extension)
        print(fn)
        with io.open(fn, 'wb') as f:
            file_handle.seek(0)
            f.write(file_handle.read())
     
