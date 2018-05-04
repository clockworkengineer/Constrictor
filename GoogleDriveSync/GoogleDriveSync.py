#!/usr/bin/env python3

"""Synchronize Google drive with local folder.

At present it only a copies the Google drive ('My Drive') and local changes are 
not reflected back on the drive. It also can handle files on the drive that 
have been removed(trashed), renamed or moved; mirroring any changes in the local
folder structure. Currently doesn't handle duplicate file names in the same folder 
well and these should be avoided(for the moment).

For setting up the crentials and secrets for use with the API it is suggsested 
that googles quickstart guide at "https://developers.google.com/drive/v3/web/quickstart/python"
be consulted.

TODO:
1) Have a local upload directory to upload files to Google drive.
2) Use worker threads to download files.
3) Use changes API better.

usage: GoogleDriveSync.py [-h] [-p POLLTIME] [-r] [-s SCOPE] [-e SECRETS]
                          [-c CREDENTIALS] [-f FILEIDCACHE] [-t TIMEZONE]
                          [-l LOGFILE]
                          folder

Synchronize Google Drive with a local folder

positional arguments:
  folder                Local folder

optional arguments:
  -h, --help            show this help message and exit
  -p POLLTIME, --polltime POLLTIME
                        Poll time for drive sychronize in minutes
  -r, --refresh         Refresh all files.
  -s SCOPE, --scope SCOPE
                        Google Drive API Scope
  -e SECRETS, --secrets SECRETS
                        Google API secrets file
  -c CREDENTIALS, --credentials CREDENTIALS
                        Google API credtials file
  -f FILEIDCACHE, --fileidcache FILEIDCACHE
                        File id cache json file
  -t TIMEZONE, --timezone TIMEZONE
                        Local timezone (pytz)
  -l LOGFILE, --logfile LOGFILE
                        All logging to file
"""

from  gdrive import GDrive
import os
import sys
import logging
import datetime
import argparse
import pytz
import json
import time
import signal

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def remove_local_file(file_name):
    """Remove file/directory from local folder."""
    
    if os.path.isfile(file_name):
        os.unlink(file_name)
        logging.info('Deleting file {} removed/renamed/moved from My Drive'.format(file_name))
        
    elif os.path.isdir(file_name):
        os.rmdir(file_name)
        logging.info('Deleting folder {} removed/renamed/moved from My Drive'.format(file_name))
                        

def rationalise_local_folder(context):
    """Clean up local folder for files removed/renamed/deleted on My Drive."""
    
    try:
        
        if os.path.exists(context.fileidcache):
            
            with open(context.fileidcache, 'r') as json_file:
                old_fileId_table = json.load(json_file)
                
            for fileId in old_fileId_table:            
                if ((fileId not in context.current_fileId_table) or 
                    (context.current_fileId_table[fileId][0] != old_fileId_table[fileId][0])):
                    remove_local_file(old_fileId_table[fileId][0])
        
    except Exception as e:
        logging.error(e)
                           
    with open(context.fileidcache, 'w') as json_file:
        json.dump(context.current_fileId_table, json_file, indent=2)
        
    context.current_fileId_table.clear()


def update_file(local_file, modified_time, local_timezone):
    """If Google drive file has been created or is newer than local file then update."""
    
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


def create_file_cache_data(context, file_data):
    """Create file id data dictionary entry."""
 
    # File data consists of a tuple (local file name, remote file mime type, remote file modification time)
    
    local_file = os.path.join(os.getcwd(), file_data['name'])
    
    # File mime type incates google app file so change local file extension for export.
    
    if file_data['mimeType'] in context.export_table:
        export_tuple = context.export_table[file_data['mimeType']]
        local_file = '{}.{}'.format(os.path.splitext(local_file)[0], export_tuple[1])
    
    context.current_fileId_table[file_data['id']] = (local_file, file_data['mimeType'], file_data['modifiedTime'])


def update_local_folder(context, my_drive):
    """Update any local files if needed."""
    
    for file_id, file_data in context.current_fileId_table.items():

        try:
                  
            if context.refresh or update_file(file_data[0], file_data[2], context.timezone):
                
                # Convert(export) any google application file  otherwise just download
                      
                if file_data[1] in context.export_table:
                    export_tuple = context.export_table[file_data[1]]
                else:
                    export_tuple = None
                         
                my_drive.file_download(file_id, file_data[0], export_tuple)
                 
        except Exception as e:
            logging.error(e)


def get_parents_children(context, drive_file_list, parent_file_id):       
    """Create a list of file data for children of of given file id"""
    
    children_list = []
    
    for file_data in drive_file_list:
        
        if parent_file_id in file_data.get('parents', []):
            children_list.append(file_data)
             
    return(children_list)

        
def traverse_drive(context, drive_file_list, file_list):
    """Recursively parse Google drive creating folders and file id data dictionary."""
    
    for file_data in file_list:

        try:
            
            # Save away current file id data
            
            create_file_cache_data(context, file_data)
                            
            # Create any needed folders and parse them recursively
            
            if file_data['mimeType'] == 'application/vnd.google-apps.folder':               
                list_results = get_parents_children(context, drive_file_list, file_data['id'])
                if not os.path.exists(file_data['name']):
                    os.mkdir(file_data['name'])
                create_file_cache_data(context, file_data)
                os.chdir(file_data['name'])
                traverse_drive(context, drive_file_list, list_results)
                os.chdir('..')
                
        except Exception as e:
            logging.error(e)
            sys.exit(1)


def synchronize_drive(context, my_drive):
        """Sychronize Google drive with local folder"""
    
        # Get full file list for drive
        
        drive_file_list = my_drive.file_list(query='not trashed',
                                             file_fields=
                                             'name, id, parents, mimeType, modifiedTime')
    
        # Get top level folder contents
        
        root_folder_id = my_drive.file_get_metadata('root')
        top_level = get_parents_children(context, drive_file_list, root_folder_id['id'])
        
        # Traverse remote drive data
        
        traverse_drive(context, drive_file_list, top_level)
        
        # Update any local files
        
        update_local_folder(context, my_drive)
        
        # Tidy up any unnecessary files left behind
        
        rationalise_local_folder(context)


def setup_signal_handlers(context):
    """Set signal handlers for SIGTERM/SIGINT so cleanly exit"""
     
    def signal_handler(signal, frame):
        logging.info('Ctrl+C entered or process terminated with kill.\nClosing down cleanly on next poll.')
        context.stop_polling = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    context.stop_polling = False

    
def load_context():
    """Load and parse command line arguments and create run context."""

    context = None
    
    try:
        
        parser = argparse.ArgumentParser(description='Synchronize Google Drive with a local folder')
        parser.add_argument('folder', help='Local folder')
        parser.add_argument('-p', '--polltime', type=int, help='Poll time for drive sychronize in minutes')
        parser.add_argument('-r', '--refresh', action='store_true', help='Refresh all files.')
        parser.add_argument('-s', '--scope', default='https://www.googleapis.com/auth/drive.readonly', help='Google Drive API Scope')
        parser.add_argument('-e', '--secrets', default='client_secret.json', help='Google API secrets file')
        parser.add_argument('-c', '--credentials', default='credentials.json', help='Google API credtials file')
        parser.add_argument('-f', '--fileidcache', default='fileID_cashe.json', help='File id cache json file')
        parser.add_argument('-t', '--timezone', default='Europe/London', help='Local timezone (pytz)')
        parser.add_argument('-l', '--logfile', help='All logging to file')
    
        context = parser.parse_args()
        
        # Set logging details
        
        logging_params = { 'level': logging.INFO}
        
        if context.logfile:
            logging_params['filename'] = context.logfile
            if not os.path.exists(os.path.dirname(context.logfile)):
                os.makedirs(os.path.dirname(context.logfile))
            
        logging.basicConfig(**logging_params)
        
        # Attach extra data to arguments to create runtime context
        
        context.timezone = pytz.timezone(context.timezone)
        context.fileId_cache_file = context.fileidcache
        context.current_fileId_table = {}
        context.drive_file_list = []
        
        #  Google App file export translation table
        
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
        
        # Create runtime context
        
        context = load_context()
        
        # Make sure on Ctrl+C program terminates cleanly
        
        setup_signal_handlers(context)
        
        logging.info('GoogleDriveSync: Sychronizing to local folder {}.'.format(context.folder))
        
        if context.refresh:
            logging.info('Refeshing whole Google drive tree locally.')
     
        # Create and intialise Google Drive API
        
        my_drive = GDrive(context.scope, context.secrets, context.credentials)
        
        my_drive.authorize()
        
        my_drive.start_service()
        
        # Create local folder root
        
        if not os.path.exists(context.folder):
            os.makedirs(context.folder)
            
        os.chdir(context.folder)
        
        # Sychronize with Google drive with local folder and keep doing if polling set
        # It also checks if any changes have been made and only synchronizes if so; it
        # is not interested in the changes themselves just that they have occured.
        
        synchronize_drive(context, my_drive)
        while context.polltime and not context.stop_polling:
            logging.info('Polling drive ....')
            time.sleep(context.polltime * 60)
            changes = my_drive.retrieve_all_changes()
            if changes:
                synchronize_drive(context, my_drive)

    except Exception as e:
        logging.error(e)
        
    logging.info('GoogleDriveSync: End of drive Sync'.format(context.folder))

        
if __name__ == '__main__':
    Main()
