#!/usr/bin/env python

"""Synchronize google drive with local folder.

At present it only provides a copy the google drive and local changes are not 
reflected back on the drive.
"""

from __future__ import print_function
from  gdrive import GDrive
import os
import logging
import datetime

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def update_file(local_file, modifiedTime):
    
    if not os.path.exists(local_file):
        print('File new{}'.format(local_file))
        return(True)
    
    times_stamp = os.path.getmtime(local_file)
    local_date_time = datetime.datetime.fromtimestamp(times_stamp)
    remote_date_time = datetime.datetime.strptime(modifiedTime[:-5], '%Y-%m-%dT%H:%M:%S')
    if remote_date_time > local_date_time:
        print('File updated {}'.format(local_file))
    return(remote_date_time > local_date_time)

    
def local_file_path(file_name, file_extension=None):
    
    local_file = os.path.join(os.getcwd(), file_name)
    
    if file_extension:
        local_file = '{}.{}'.format(os.path.splitext(local_file)[0], file_extension)
    
    return(local_file)

    
def traverse(my_drive, file_list):
    
    for file_data in file_list:

        if file_data['mimeType'] == 'application/vnd.google-apps.folder':
            query = "('{}' in parents) and (not trashed)".format(file_data['id'])
            list_results = my_drive.file_list(query, file_fields='name, id, parents, mimeType, modifiedTime')
            if not os.path.exists(file_data['name']):
                os.mkdir(file_data['name'])
            os.chdir(file_data['name'])
            traverse(my_drive, list_results)
            os.chdir('..')
        elif file_data['mimeType'] == 'application/vnd.google-apps.document':
            local_file = local_file_path(file_data['name'], 'pdf')
            if update_file(local_file, file_data['modifiedTime']):
                my_drive.file_export(file_data['id'], local_file, 'application/pdf', 'pdf')
        elif file_data['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            local_file = local_file_path(file_data['name'], 'xlsx')
            if update_file(local_file, file_data['modifiedTime']):
                my_drive.file_export(file_data['id'], local_file, 'application/pdf', 'xlsx')
        else:
            local_file = local_file_path(file_data['name'])
            if update_file(local_file, file_data['modifiedTime']):
                my_drive.file_download(file_data['id'], local_file)

####################
# Main Entry Point #
####################


def main():
    
#     logging.basicConfig(level=logging.INFO)
 
    my_drive = GDrive('https://www.googleapis.com/auth/drive.readonly',
                      'client_secret.json', 'credentials.json')
    
    my_drive.authorize()
    
    my_drive.start_service()
    
    list_results = my_drive.file_list("('root' in parents) and (not trashed)",
                                      file_fields='name, id, parents, mimeType, modifiedTime')
    
    os.chdir('/home/robt/ftproot')
    
    traverse(my_drive, list_results)


if __name__ == '__main__':
    main()
