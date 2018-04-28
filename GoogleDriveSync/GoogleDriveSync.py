#!/usr/bin/env python3

"""Synchronize google drive with local folder.

At present it only a copies the google drive ('My Drive') and local changes are 
not reflected back on the drive.
"""

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


def remove_local_file(file_name):
    """ Remove file/directory from local folder"""
    
    if os.path.isfile(file_name):
        os.unlink(file_name)
        logging.info('Deleting file {} removed/renamed/moved from My Drive'.format(file_name))
        
    elif os.path.isdir(file_name):
        os.rmdir(file_name)
        logging.info('Deleting folder {} removed/renamed/moved from My Drive'.format(file_name))
                        

def rationalise_local_folder(context):
    """Clean up local folder for files removed/renamed/deleted on My Drive"""
    
    try:
        
        if os.path.exists(context.fileidcache):
            
            with open(context.fileidcache, 'r') as json_file:
                _old_fileId_table = json.load(json_file)
                
            for fileId in _old_fileId_table:            
                if ((fileId not in context.current_fileId_table) or 
                    (context.current_fileId_table[fileId] != _old_fileId_table[fileId])):
                    remove_local_file(_old_fileId_table[fileId])
        
    except Exception as e:
        logging.error(e)
                           
    with open(context.fileidcache, 'w') as json_file:
        json.dump(context.current_fileId_table, json_file, indent=2)


def update_file(local_file, modified_time, local_timezone):
    """If 'My Drive' file has been created or is newer than local file then update."""
    
    try:

        if not os.path.exists(local_file):
            logging.info('File {} does not exist locally.'.format(local_file))
            return(True)
        
        # Make sure timestamp is in utc for when both are localized and compared
        
        times_stamp = os.path.getmtime(local_file)
        local_date_time = local_timezone.localize(datetime.datetime.utcfromtimestamp(times_stamp)) 
        remote_date_time = local_timezone.localize(datetime.datetime.strptime(modified_time[:-5], '%Y-%m-%dT%H:%M:%S'))

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

    
def traverse_drive(context, my_drive, file_list):
    """Recursively parse 'My Drive' creating folders and downloading files"""
    
    for file_data in file_list:

        try:
            
            # Create any needed folders and parse then recursively
            
            if file_data['mimeType'] == 'application/vnd.google-apps.folder':               
                query = "('{}' in parents) and (not trashed)".format(file_data['id'])
                list_results = my_drive.file_list(query, file_fields='name, id, parents, mimeType, modifiedTime')
                if not os.path.exists(file_data['name']):
                    os.mkdir(file_data['name'])
                os.chdir(file_data['name'])
                context.current_fileId_table[file_data['id']] = os.getcwd()
                traverse_drive(context, my_drive, list_results)
                os.chdir('..')
                
            # Export any google application file
            
            elif file_data['mimeType'] in context.export_table:
                export_tuple = context.export_table[file_data['mimeType']]
                local_file = local_file_path(file_data['name'], export_tuple[1])
                context.current_fileId_table[file_data['id']] = local_file
                if context.refresh or update_file(local_file, file_data['modifiedTime'], context.timezone):
                    my_drive.file_export(file_data['id'], local_file, export_tuple[0])
                    
            # Download file as is
                      
            else:
                local_file = local_file_path(file_data['name'])
                context.current_fileId_table[file_data['id']] = local_file
                if context.refresh or update_file(local_file, file_data['modifiedTime'], context.timezone):
                    my_drive.file_download(file_data['id'], local_file)
                
        except Exception as e:
            logging.error(e)

    
def load_context():
    """Load and parse command line arguments and create run context"""
    
    global _timezone, _fileId_cache_file
    
    context = None
    
    try:
        
        parser = argparse.ArgumentParser(description='Synchronize Google Drive with a local folder')
        parser.add_argument('folder', help='Local folder')
        parser.add_argument('-r', '--refresh', action='store_true', help='Refresh all files.')
        parser.add_argument('-s', '--scope', default='https://www.googleapis.com/auth/drive.readonly', help='Google Drive API Scope')
        parser.add_argument('-e', '--secrets', default='client_secret.json', help='Google API secrets file')
        parser.add_argument('-c', '--credentials', default='credentials.json', help='Google API credtials file')
        parser.add_argument('-f', '--fileidcache', default='fileID_cashe.json', help='File id cache json file')
        parser.add_argument('-t', '--timezone', default='Europe/London', help='Local timezone (pytz)')
    
        context = parser.parse_args()
        
        # Attach extra data to arguments to create runtime context
        
        context.timezone = pytz.timezone(context.timezone)
        context.fileId_cache_file = context.fileidcache
        context.current_fileId_table = {}
        
        context.export_table = { 
                          'application/vnd.google-apps.document' : 
                          ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx'),
                          'application/vnd.google-apps.spreadsheet' : 
                          ('application/vnd.oasis.opendocument.spreadsheet', 'ods'),
                          'application/vnd.google-apps.presentation' : 
                          ('application/vnd.oasis.opendocument.presentation', 'odp')
                        }
         
    except Exception as e:
        logging.error(e)
        sys.exit(1)
         
    return(context)

####################
# Main Entry Point #
####################


def Main():
    
    try:
        
        logging.basicConfig(level=logging.INFO)
        
        # Creat runtime context
        
        context = load_context()
        
        logging.info('GoogleDriveSync: Sychronizing to local folder {}.'.format(context.folder))
        
        if context.refresh:
            logging.info('Refeshing whole Google drive tree locally.')
     
        # Create and intialise Google Drive API
        
        my_drive = GDrive(context.scope, context.secrets, context.credentials)
        
        my_drive.authorize()
        
        my_drive.start_service()
        
        # Get top level folder contexts
        
        top_level = my_drive.file_list("('root' in parents) and (not trashed)",
                                          file_fields='name, id, parents, mimeType, modifiedTime')
        
        # Create local folder root
        
        if not os.path.exists(context.folder):
            os.makedirs(context.folder)
            
        os.chdir(context.folder)
        
        # Traverse remote drive data and create local copy
        
        traverse_drive(context, my_drive, top_level)
        
        # Tidy up any unnecessary files left behind
        
        rationalise_local_folder(context)
        
        logging.info('GoogleDriveSync: End of drive Sync'.format(context.folder))

    except Exception as e:
        logging.error(e)

        
if __name__ == '__main__':
    Main()