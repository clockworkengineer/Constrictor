#!/usr/bin/env python

"""Synchronize google drive with local folder.

At present it only a copies the google drive ('My Drive') and local changes are 
not reflected back on the drive.
"""

from __future__ import print_function
from  gdrive import GDrive
import os
import sys
import logging
import datetime
import argparse
import pytz
import json

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"

################################################################################
#                                Globals                                       #
################################################################################

# Mapping table used when exporting google application files

_export_table = { 'application/vnd.google-apps.document' : 
                  ('application/pdf', 'pdf'),
                  'application/vnd.google-apps.spreadsheet' : 
                  ('application/vnd.oasis.opendocument.spreadsheet', 'ods'),
                  'application/vnd.google-apps.presentation' : 
                  ('application/vnd.oasis.opendocument.presentation', 'odp')
                }

# Current timezone

_timezone = None;

# Mapping between file id and local file paths

_current_fileId_table = {}

# JSON cache file name

_fileId_cache_file = None


def remove_local_file(file_name):
    """ Remove file/directory from local folder"""
    
    if os.path.isfile(file_name):
        os.unlink(file_name)
        logging.info('Deleting file {} removed/renamed/moved from My Drive'.format(file_name))
    elif os.path.isdir(file_name):
        os.rmdir(file_name)
        logging.info('Deleting folder {} removed/renamed/moved from My Drive'.format(file_name))
                        

def rationalise_local_folder():
    """Clean up local folder for files removed/renamed/deleted on My Drive"""
    
    try:
        
        if os.path.exists(_fileId_cache_file):
            with open(_fileId_cache_file, 'r') as json_file:
                _old_fileId_table = json.load(json_file)
                
            for fileId in _old_fileId_table:
                
                if ((fileId not in _current_fileId_table) or 
                    (_current_fileId_table[fileId] != _old_fileId_table[fileId])):
                    remove_local_file(_old_fileId_table[fileId])
        
    except Exception as e:
        logging.error(e)
                           
    with open(_fileId_cache_file, 'w') as json_file:
        json.dump(_current_fileId_table, json_file, indent=2)


def update_file(local_file, modified_time):
    """If 'My Drive' file has been created or is newer than local file then update."""
    
    try:

        if not os.path.exists(local_file):
            logging.info('File {} does not exist locally.'.format(local_file))
            return(True)
        
        # Make sure timestamp is in utc for when both are localized and compared
        
        times_stamp = os.path.getmtime(local_file)
        local_date_time = _timezone.localize(datetime.datetime.utcfromtimestamp(times_stamp)) 
        remote_date_time = _timezone.localize(datetime.datetime.strptime(modified_time[:-5], '%Y-%m-%dT%H:%M:%S'))

        if remote_date_time > local_date_time:
            logging.info('File {} needs updating locally.'.format(local_file))
        
    except Exception as e:
        logging.error(e)
        return(False)
        
    return(remote_date_time > local_date_time)

    
def local_file_path(file_name, file_extension=None):
    """Create local file name for 'My Drive' file."""
    
    local_file = os.path.join(os.getcwd(), file_name)
    
    if file_extension:
        local_file = '{}.{}'.format(os.path.splitext(local_file)[0], file_extension)
    
    return(local_file)

    
def traverse_drive(my_drive, file_list, refresh=False):
    """Recursively parse 'My Drive' creating folders and downloading files"""
    
    for file_data in file_list:

        try:
            
            if file_data['mimeType'] == 'application/vnd.google-apps.folder':
                query = "('{}' in parents) and (not trashed)".format(file_data['id'])
                list_results = my_drive.file_list(query, file_fields='name, id, parents, mimeType, modifiedTime')
                if not os.path.exists(file_data['name']):
                    os.mkdir(file_data['name'])
                os.chdir(file_data['name'])
                _current_fileId_table[file_data['id']] = os.getcwd()
                traverse_drive(my_drive, list_results, refresh)
                os.chdir('..')
            elif file_data['mimeType'] in _export_table:
                export_tuple = _export_table[file_data['mimeType']]
                local_file = local_file_path(file_data['name'], export_tuple[1])
                _current_fileId_table[file_data['id']] = local_file
                if refresh or update_file(local_file, file_data['modifiedTime']):
                    my_drive.file_export(file_data['id'], local_file, export_tuple[0])          
            else:
                local_file = local_file_path(file_data['name'])
                _current_fileId_table[file_data['id']] = local_file
                if refresh or update_file(local_file, file_data['modifiedTime']):
                    my_drive.file_download(file_data['id'], local_file)
                
        except Exception as e:
            logging.error(e)

    
def load_arguments():
    """Load and parse command line arguments"""
    
    global _timezone, _fileId_cache_file
    
    arguments = None
    
    try:
        
        parser = argparse.ArgumentParser(description='Synchronize Google Drive with a local folder')
        parser.add_argument('folder', help='Local folder')
        parser.add_argument('-r', '--refresh', action='store_true', help='Refresh all files.')
        parser.add_argument('-s', '--scope', default='https://www.googleapis.com/auth/drive.readonly', help='Google Drive API Scope')
        parser.add_argument('-e', '--secrets', default='client_secret.json', help='Google API secrets file')
        parser.add_argument('-c', '--credentials', default='credentials.json', help='Google API credtials file')
        parser.add_argument('-f', '--fileidcache', default='fileID_cashe.json', help='File id cache json file')
        parser.add_argument('-t', '--timezone', default='Europe/London', help='Local timezone (pytz)')
    
        arguments = parser.parse_args()
        
        # Use globals for now
        
        _timezone = pytz.timezone(arguments.timezone)
        _fileId_cache_file = arguments.fileidcache
    
    except Exception as e:
        logging.error(e)
        sys.exit(1)
         
    return(arguments)

####################
# Main Entry Point #
####################


def main():
    
    try:
        
        logging.basicConfig(level=logging.INFO)
        
        arguments = load_arguments()
        
        logging.info('GoogleDriveSync: Sychronizing to local folder {}.'.format(arguments.folder))
        
        if arguments.refresh:
            logging.info('Refeshing whole Google drive tree locally.')
     
        my_drive = GDrive(arguments.scope, arguments.secrets, arguments.credentials)
        
        my_drive.authorize()
        
        my_drive.start_service()
        
        top_level = my_drive.file_list("('root' in parents) and (not trashed)",
                                          file_fields='name, id, parents, mimeType, modifiedTime')
        
        if not os.path.exists(arguments.folder):
            os.makedirs(arguments.folder)
            
        os.chdir(arguments.folder)
        
        traverse_drive(my_drive, top_level, arguments.refresh)
        
        rationalise_local_folder()
        
        logging.info('GoogleDriveSync: End of drive Sync'.format(arguments.folder))

    except Exception as e:
        logging.error(e)

        
if __name__ == '__main__':
    main()
