#!/usr/bin/env python3
"""Synchronize Google drive with local folder.

At present it only a copies the Google drive ('My Drive') and local changes are 
not reflected back on the drive. It also can handle files on the drive that 
have been removed(trashed), renamed or moved; mirroring any changes in the local
folder structure. Currently doesn't handle duplicate file names in the same Google
Drive folder well and these should be avoided (for the moment).

For setting up the crentials and secrets for use with the API it is suggsested 
that googles quickstart guide at "https://developers.google.com/drive/v3/web/
quickstart/python" be consulted.

TODO:
1) Use changes API better
2) Compress file id cache file
3) Better exception handling

usage: GoogleDriveSync.py [-h] [-p POLLTIME] [-r] [-s SCOPE] [-e SECRETS]
                          [-c CREDENTIALS] [-f FILEIDCACHE] [-t TIMEZONE]
                          [-l LOGFILE] [-n NUMWORKERS] [-u UPLOADFOLDER]
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
  -n NUMWORKERS, --numworkers NUMWORKERS
                        Number of worker threads for downloads
  -u UPLOADFOLDER, --uploadfolder UPLOADFOLDER
                        Google upload folder
"""

from localdrive import LocalDrive, RemoteDrive
from  gdrive import GAuthorize, GDriveUploader
import os
import sys
import logging
import argparse
import signal

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def synchronize_drive(context, remote_drive):
        """Sychronize Google drive with local drive folder"""
        
        # Create and build local folder for Google drive
        
        local_drive = LocalDrive(context.folder, remote_drive)
          
        if context.numworkers:
            local_drive.set_numworkers(context.numworkers)
        
        if context.refresh:
            local_drive.set_refresh(context.refresh)
            
        if context.fileidcache:
            local_drive.set_fileidcache(context.fileidcache)
            
        if context.timezone:
            local_drive.set_timezone(context.timezone)
            
        local_drive.build()
        
        # Update any local files
        
        local_drive.update()
        
        # Tidy up any unnecessary files left behind
        
        local_drive.rationalise()


def create_file_uploader(context, credentials):
    """Create uploader folder for Google Drive"""
    
    uploader = GDriveUploader(credentials, context.uploadfolder, os.path.basename(context.uploadfolder))
    
    logging.info("Created upload folder {} for Google drive.".format(context.uploadfolder))


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
        parser.add_argument('-f', '--fileidcache', help='File id cache json file')
        parser.add_argument('-t', '--timezone', help='Local timezone (pytz)')
        parser.add_argument('-l', '--logfile', help='All logging to file')
        parser.add_argument('-n', '--numworkers', type=int, help='Number of worker threads for downloads')
        parser.add_argument('-u', '--uploadfolder', help='Google upload folder')
    
        context = parser.parse_args()
        
        # Set logging details
        
        logging_params = { 'level': logging.INFO}
        
        if context.logfile:
            logging_params['filename'] = context.logfile
            if not os.path.exists(os.path.dirname(context.logfile)):
                os.makedirs(os.path.dirname(context.logfile))
            
        logging.basicConfig(**logging_params)

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
     
        # Authorize application with Google
        
        credentials = GAuthorize('https://www.googleapis.com/auth/drive', context.secrets, context.credentials)
        
        if not credentials:
            logging.error('GoogleDriveSync: Could not perform authorization')
            sys.exit(1)
            
        # Create RemoteDrive object
        
        remote_drive = RemoteDrive(credentials)
        
        # Create file uploader object
        
        if context.uploadfolder:
            create_file_uploader(context, credentials)
        
        # Sychronize with Google drive with local folder and keep doing if polling set
        # It also checks if any changes have been made and only synchronizes if so; it
        # is not interested in the changes themselves just that they have occured.
        
        synchronize_drive(context, remote_drive)
        while context.polltime and not context.stop_polling:
            logging.info('Polling drive ....')
            time.sleep(context.polltime * 60)
            changes = remote_drive.retrieve_all_changes()
            if changes:
                synchronize_drive(context, remote_drive)

    except Exception as e:
        logging.error(e)
        
    logging.info('GoogleDriveSync: End of drive Sync'.format(context.folder))

        
if __name__ == '__main__':

    Main()
