#!/usr/bin/env python3
"""Synchronize Google drive with local folder.

At present it only a copies the Google drive ('My Drive') and local changes are 
not reflected back on the drive. It also can handle files on the drive that 
have been removed(trashed), renamed or moved; mirroring any changes in the local
folder structure. Currently doesn't handle duplicate file names in the same Google
Drive folder well and these should be avoided (for the moment). Note: When referencing
the comments Remote drive and Google drive are the same thing.

For setting up the crentials and secrets for use with the API it is suggsested 
that googles quickstart guide at "https://developers.google.com/drive/v3/web/
quickstart/python" be consulted.

usage: GoogleDriveSync.py [-h] [-p POLLTIME] [-r] [-s SCOPE] [-e SECRETS]
                          [-c CREDENTIALS] [-f FILEIDCACHE] [-t TIMEZONE]
                          [-l LOGFILE] [-o LOGLEVEL] [-a TRANSLATOR]
                          [-n NUMWORKERS] [-u UPLOADFOLDER]
                          [-i IGNORELIST [IGNORELIST ...]] [-b]
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
                        File id cache pickle file
  -t TIMEZONE, --timezone TIMEZONE
                        Local timezone (pytz)
  -l LOGFILE, --logfile LOGFILE
                        All logging to file
  -o LOGLEVEL, --loglevel LOGLEVEL
                        Logging Level
  -a TRANSLATOR, --translator TRANSLATOR
                        File translator json file
  -n NUMWORKERS, --numworkers NUMWORKERS
                        Number of worker threads for downloads
  -u UPLOADFOLDER, --uploadfolder UPLOADFOLDER
                        Google upload folder
  -i IGNORELIST [IGNORELIST ...], --ignorelist IGNORELIST [IGNORELIST ...]
                        Ignore file/path list
  -b, --forcerefresh    Force refresh of remote file cache on each poll.
  
TODO:
1) Expand file translation table.
2) Unix daemonize.
3) PyInstaller (?)
"""

from localdrive import LocalDrive
from remotedrive import RemoteDrive
from gdrive import g_authorize, GDriveError
import os
import sys
import logging
import argparse
import signal
import time
import filetranslator

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def setup_signal_handlers(context):
    """Set signal handlers for SIGTERM/SIGINT so cleanly exit.
    
    Redirect Control-C and kill process to set global flag stop polling and thus cleanly
    exit program on next synchronize poll loop.
    
    Arguments:
        context:    runtime context (globlals/arguments)
    """

    def signal_handler(signal_number, frame):
        logging.info('Ctrl+C entered or process terminated with kill.\nClosing down cleanly on next poll.')
        context.continue_polling = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def load_context():
    """Load and parse command line arguments and create runtime context.
    
    Parse command line arguments and create runtime context. Also set any
    logging parameters passed in (just to file for the moment).
    
    Returns:
        context:    runtime parameters
    """

    context = None

    try:

        parser = argparse.ArgumentParser(description='Synchronize Google Drive with a local folder')
        parser.add_argument('folder', help='Local folder')
        parser.add_argument('-p', '--polltime', type=int, default=0, help='Poll time for drive sychronize in minutes')
        parser.add_argument('-r', '--refresh', action='store_true', default=False, help='Refresh all files.')
        parser.add_argument('-s', '--scope', default='https://www.googleapis.com/auth/drive.readonly',
                            help='Google Drive API Scope')
        parser.add_argument('-e', '--secrets', default='client_secret.json', help='Google API secrets file')
        parser.add_argument('-c', '--credentials', default='credentials.json', help='Google API credtials file')
        parser.add_argument('-f', '--fileidcache', default='fileID_cache.P', help='File id cache pickle file')
        parser.add_argument('-t', '--timezone', default='Europe/London', help='Local timezone (pytz)')
        parser.add_argument('-l', '--logfile', help='All logging to file')
        parser.add_argument('-o', '--loglevel', default=logging.INFO, type=int, help='Logging Level')
        parser.add_argument('-a', '--translator', default='file_translator.json', help='File translator json file')
        parser.add_argument('-n', '--numworkers', type=int, default=4, help='Number of worker threads for downloads')
        parser.add_argument('-u', '--uploadfolder', help='Google upload folder')
        parser.add_argument('-i', '--ignorelist', nargs='+', default=[], help='Ignore file/path list')
        parser.add_argument('-b', '--forcerefresh', action='store_true', default=False,
                            help='Force refresh of remote file cache on each poll.')

        context = parser.parse_args()

        # If poltime zero then only synchronize once

        context.continue_polling = (context.polltime != 0)

        # Set logging details

        logging_params = {'level': context.loglevel,
                          'format': '%(asctime)s:GoogleDriveSync:%(message)s'}

        if context.logfile:
            logging_params['filename'] = context.logfile
            if not os.path.exists(os.path.dirname(context.logfile)):
                os.makedirs(os.path.dirname(context.logfile))

        logging.basicConfig(**logging_params)

        logging.info('Logging intialised with parameters({}).'.format(logging_params))

    except Exception as e:
        logging.error(e)
        sys.exit(1)

    return context


####################
# Main Entry Point #
####################


def google_drive_sync():
    """GoogleDriveSync main program entry point."""

    try:

        # Create runtime context

        context = load_context()

        # Make sure on Ctrl+C program terminates cleanly

        setup_signal_handlers(context)

        logging.info('Sychronizing to local folder {}.'.format(context.folder))

        if context.refresh:
            logging.info('Refeshing whole Google drive tree locally.')

        # Authorize application with Google

        credentials = g_authorize(context.scope, context.secrets, context.credentials)

        if not credentials:
            logging.error('Could not perform authorization')
            sys.exit(1)

        logging.info('Authorization sucess.')

        # Create file translator

        file_translator = filetranslator.FileTranslator(context.translator)

        # Create RemoteDrive / LocalDrive objects

        remote_drive = RemoteDrive(credentials, context.uploadfolder, file_translator, context.forcerefresh)

        local_drive = LocalDrive(context.folder, remote_drive, file_translator)

        local_drive.numworkers = context.numworkers
        local_drive.refresh = context.refresh
        local_drive.fileidcache = context.fileidcache
        local_drive.timezone = context.timezone
        local_drive.ignorelist = context.ignorelist
        local_drive.load_file_id_cache_from_file()

        # Sychronize Google Drive with local folder and keep doing if polling enabled

        local_drive.synchronize()
        while context.continue_polling:
            logging.info('Polling drive ....')
            time.sleep(context.polltime * 60)
            local_drive.synchronize()

        local_drive.write_file_id_cache_to_file()

    except (Exception, GDriveError) as e:
        logging.error(e)

    logging.info('End of drive Sync.')


if __name__ == '__main__':
    google_drive_sync()
