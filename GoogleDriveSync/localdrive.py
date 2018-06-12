"""Class for accessing local drive.

Map google drive to local file system folder keeping there remote file directory 
structure.
"""

from gdrive import GDrive, GDriveError
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import logging
import datetime
import pytz
import time
import collections
import cloudpickle

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class LocalDrive(object):
    """Class representing local file system mirrior of Google drive.
    
    Create mirror Google drive on local file system.
     
    Attributes:
        _local_root_path:        Local filesystem root folder
        _remote_drive:           Remote drive object
        _current_file_id_cache:  Current file Id data cache (dictionary)
        _old_file_id_cache:      Old file Id data cache (dictionary)
        _File_Data:              Named tuple for file cache data
        _file_translator         File translator
        refresh:                 == True then complete refresh
        timezone:                Time zone used in file modified time compares
        numworkers:              Number of worker download threads
        fileidcache:             File name for file id cache
        ignorelist:              Local files/path not included in any synchronize
    """

    def __init__(self, local_root_path, remote_drive, file_translator):

        self._local_root_path = local_root_path
        self._remote_drive = remote_drive
        self._current_file_id_cache = {}
        self._old_file_id_cache = {}
        self._download_errors = 0
        self._File_Data = collections.namedtuple('File_Data', 'file_name mime_type modified_time, file_size')
        self._file_translator = file_translator

        # Create local folder root

        if not os.path.exists(self._local_root_path):
            os.makedirs(self._local_root_path)

    def load_file_id_cache_from_file(self):
        """Load old file id cache."""

        if os.path.exists(self.fileidcache):
            with open(self.fileidcache, 'rb') as file_id_cache_file:
                self._old_file_id_cache = cloudpickle.load(file_id_cache_file)

    def write_file_id_cache_to_file(self):
        """Save current file id cache."""

        with open(self.fileidcache, 'wb') as file_id_cache_file:
            cloudpickle.dump(self._old_file_id_cache, file_id_cache_file)

    def _set_file_cache_data(self, local_file, file_data):
        """Create file id data cache object"""

        file_size = int(file_data.get('size', 0))

        # Google docs have zero size so fake so they are downloaded and not created like normal zero sized files.

        if file_size == 0 and file_data['mimeType'].startswith('application/vnd.google-apps'):
            file_size = -1

        return self._File_Data(file_name=local_file,
                               mime_type=file_data['mimeType'],
                               modified_time=file_data['modifiedTime'],
                               file_size=file_size)

    def _create_file_id_cache_entry(self, current_directory, file_data):
        """Create file id cache entry."""

        # Create local path name

        local_file = os.path.join(current_directory, file_data['name'])

        # Ignore local folder paths on ignore list (ie. upload folder;so that contents don't get copied).

        for ignore_file in self._ignorelist:
            if local_file.startswith(ignore_file):
                logging.debug("Ignoring file {}.".format(local_file))
                return

        # File mime type incates google app file so change local file extension for export.

        if self._file_translator.remote_mime_type_mapped(file_data['mimeType']):
            local_file = '{}.{}'.format(os.path.splitext(local_file)[0],
                                        self._file_translator.get_local_file_extension(file_data['mimeType']))

        self._current_file_id_cache[file_data['id']] = self._set_file_cache_data(local_file, file_data)

        logging.debug(
            'Created file id cache entry {} : {}.'.format(file_data['id'],
                                                          self._current_file_id_cache[file_data['id']]))

    def _get_parents_children(self, parent_file_id):
        """Create a list of file data for children of of given file id"""

        children_list = []

        for file_data in self._remote_drive.file_cache:

            if parent_file_id in file_data.get('parents', []):
                children_list.append(file_data)

        return children_list

    def _traverse(self, current_directory, file_list):
        """Recursively parse Google drive creating folders and file id data dictionary."""

        for file_data in file_list:

            try:

                # Save away current file id data

                self._create_file_id_cache_entry(current_directory, file_data)

                # If current file a folder then recursivelt parse

                if file_data['mimeType'] == 'application/vnd.google-apps.folder':
                    siblings_list = self._get_parents_children(file_data['id'])
                    self._traverse(os.path.join(current_directory, file_data['name']), siblings_list)

            except Exception as e:
                logging.error(e)
                sys.exit(1)

    def _build(self):
        """Build file Id cache for remote drive."""

        try:

            # Clear current file id cache

            self._current_file_id_cache.clear()

            # Get top level folder contents

            top_level = self._get_parents_children(self._remote_drive.root_folder_id)

            # Traverse remote drive file cache

            self._traverse(self._local_root_path, top_level)

        except Exception as e:
            logging.error(e)
            sys.exit(1)

    @staticmethod
    def _update_file(local_file, modified_time, local_timezone):
        """If Google drive file has been created or is newer than local file then _update."""

        try:

            if not os.path.exists(local_file):
                return True

            # Make sure timestamp is in utc for when both are localized and compared

            times_stamp = os.path.getmtime(local_file)
            local_date_time = local_timezone.localize(datetime.datetime.utcfromtimestamp(times_stamp))
            remote_date_time = local_timezone.localize(datetime.datetime.strptime(modified_time[:-5],
                                                                                  '%Y-%m-%dT%H:%M:%S'))

        except Exception as e:
            logging.error(e)
            return False

        return remote_date_time > local_date_time

    def _download_worker(self, file_id, local_file, mime_type, sleep_delay=1):
        """Download file worker thread."""

        # For moment create new GDrive as http module used by underlying api is
        # not multi-thread aware and also add delay in for google 403 error if more
        # than approx 8 requests a second are made.
        #
        # TO DO: Get rid of delay and GDrive creation for each download.

        try:
            drive = GDrive(self._remote_drive.credentials)
            drive.file_download(file_id, local_file, mime_type)
            time.sleep(sleep_delay)
        except GDriveError as e:
            logging.error(e)
            self._download_errors += 1

    def _update(self):
        """Update any local files if needed."""

        file_list = []
        empty_file_list = []

        for file_id, file_data in self._current_file_id_cache.items():

            try:

                # Create any folders needed

                if file_data.mime_type == "application/vnd.google-apps.folder":
                    if not os.path.exists(file_data.file_name):
                        os.makedirs(file_data.file_name)
                    continue

                if self._refresh or self._update_file(file_data.file_name, file_data.modified_time, self.timezone):

                    # Do not download empty files

                    if file_data.file_size != 0:

                        # Convert(export) any google application file  otherwise just download

                        if self._file_translator.remote_mime_type_mapped(file_data.mime_type):
                            mime_type = self._file_translator.get_local_mime_type(file_data.mime_type)
                        else:
                            mime_type = None

                        file_list.append((file_id, file_data.file_name, mime_type))

                    else:
                        empty_file_list.append(file_data.file_name)

            except Exception as e:
                logging.error(e)
                sys.exit(1)

        # If worker threads > 1 then use otherwise one at a time

        if self._numworkers > 1:

            with ThreadPoolExecutor(max_workers=self._numworkers) as executor:
                for file_to_process in file_list:
                    executor.submit(self._download_worker, *file_to_process)

        else:

            try:
                for file_to_process in file_list:
                    self._remote_drive.file_download(*file_to_process)
            except GDriveError:
                self._download_errors += 1

        # Empty files are not downloaded but created locally as placeholders

        if empty_file_list:
            for empty_file in empty_file_list:
                open(empty_file, 'w').close()
                logging.info('Created empty local file {}.'.format(empty_file))

        if self._download_errors:
            logging.info('{} errors during file downloads.'.format(self._download_errors))
            self._download_errors = 0

    @staticmethod
    def _remove_local_file(file_name):
        """Remove file/directory from local folder."""

        if os.path.isfile(file_name):
            os.unlink(file_name)
            logging.info('Deleting file {} removed/renamed/moved from My Drive'.format(file_name))

        elif os.path.isdir(file_name):
            os.rmdir(file_name)
            logging.info('Deleting folder {} removed/renamed/moved from My Drive'.format(file_name))

    def _rationalise(self):
        """Clean up local folder for files removed/renamed/deleted on My Drive."""

        try:

            if self._old_file_id_cache:

                for fileId in self._old_file_id_cache:
                    if ((fileId not in self._current_file_id_cache) or
                            (self._current_file_id_cache[fileId].file_name != self._old_file_id_cache[
                                fileId].file_name)):
                        self._remove_local_file(self._old_file_id_cache[fileId].file_name)

        except Exception as e:
            logging.error(e)

    def synchronize(self):
        """Synchronize local folder from remote drive."""

        # Check for remote drive changes (_current_file_id_cache == {} then first synchronize)

        if (not self._current_file_id_cache) or self._remote_drive.has_changed():

            logging.info('Syncing changes....')

            # Build file Id cache

            self._build()

            # Update any local files

            self._update()

            # Tidy up any unnecessary files left behind

            self._rationalise()

            #  Copy current file id cache

            self._old_file_id_cache = self._current_file_id_cache.copy()

        else:
            logging.info('No changes present.')

    # Properties

    @property
    def refresh(self):
        return self._refresh

    @refresh.setter
    def refresh(self, refresh):
        self._refresh = refresh

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        self._timezone = pytz.timezone(timezone)

    @property
    def numworkers(self):
        return self._numworkers

    @numworkers.setter
    def numworkers(self, numworkers):
        self._numworkers = numworkers

    @property
    def fieldidcache(self):
        return self._fileidcache

    @fieldidcache.setter
    def fieldidcache(self, fieldidcache):
        self._fileidcache = fieldidcache

    @property
    def ignorelist(self):
        return self.ignorelist

    @ignorelist.setter
    def ignorelist(self, ignorelist):
        self._ignorelist = ignorelist
