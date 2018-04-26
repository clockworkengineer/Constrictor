"""Synchronize google drive with local folder.

At present it only provides a copy the google drive and local changes are not 
reflected back on the drive.
"""
from __future__ import print_function
from  gdrive import GDrive
import os


def traverse(file_list):
    
    for file_data in file_list:
        
        if file_data['mimeType'] == 'application/vnd.google-apps.folder':
            query = "('{}' in parents) and (not trashed)".format(file_data['id'])
            list_results = my_drive.file_list(query, file_fields='name, id, parents, mimeType')
            if not os.path.exists(file_data['name']):
                os.mkdir(file_data['name'])
            os.chdir(file_data['name'])
            traverse(list_results)
            os.chdir('..')
        elif file_data['mimeType'] == 'application/vnd.google-apps.document':
            local_file = os.path.join(os.getcwd(), file_data['name'])
            my_drive.file_export(file_data['id'], local_file, 'application/pdf', 'pdf')
        elif file_data['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            local_file = os.path.join(os.getcwd(), file_data['name'])
            my_drive.file_export(file_data['id'], local_file, 'application/pdf', 'xlsx')
        else:
            local_file = os.path.join(os.getcwd(), file_data['name'])
            my_drive.file_download(file_data['id'], local_file)

    
my_drive = GDrive('https://www.googleapis.com/auth/drive.readonly',
                  'client_secret.json', 'credentials.json')

my_drive.authorize()

my_drive.start_service()

list_results = my_drive.file_list("('root' in parents) and (not trashed)", file_fields='name, id, parents, mimeType')

os.chdir('/home/robt/ftproot')

traverse(list_results)

