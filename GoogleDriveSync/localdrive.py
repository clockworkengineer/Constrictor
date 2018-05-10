"""Class for accessing local drive.

Class to map google drive to local file system.
"""

from  gdrive import GDrive
from concurrent.futures import ThreadPoolExecutor
import os
import sys
import logging
import datetime
import json
import pytz
import time

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class RemoteDrive(GDrive):
    """Class to access Google drive.
    
    Access Google drive files (keeping a complete file cache locally).
    
    Attrubutes:
    file_cache:         Drive file cache.
    root_folder_id:     File ID for root folder.
    """
    
    def __init__(self, credentials):
        
        try:
            
            super().__init__(credentials)
            
            # Get all files not in trash for cache
            
            self.file_cache = self.file_list(query='not trashed',
                                                 file_fields=
                                                 'name, id, parents, mimeType, modifiedTime')
            
            self.root_folder_id = self.file_get_metadata('root')

        except Exception as e:
            logging.error(e)
    
    # Properties
     
    @property
    def file_cache_id(self):
        return(self._file_cache_id)
    
    @file_cache_id.setter
    def file_cache_id(self, file_cache_id):
        self._file_cache_id = file_cache_id
        
    @property
    def root_folder_id(self):
        return(self._root_folder_id)
    
    @file_cache_id.setter
    def root_folder_id(self, root_folder_id):
        self._root_folder_id = root_folder_id

               
class LocalDrive(object):
    """Class representing local file system mirrior of Google drive.
    
    Create mirror Google drive on local file system.
     
    Attributes:
    _local_root_path:         Local filesystem root folder
    _remote_drive:            Remote drive object
    _current_fileId_table:    File Id data cache (dictionary)
    refresh:                 == True then complete refresh
    timezone:                Time zone used in file modified time compares
    numworkers:              Number of worker download threads
    fileidcache:             File name for file id cache
    """
     
    def __init__(self, local_root_path, remote_drive):
         
        self._local_root_path = local_root_path
        self._remote_drive = remote_drive
        self._current_fileId_table = {}
        self._download_errors = 0
              
        self.refresh = False
        self.timezone = 'Europe/London'
        self.numworkers = 4
        self.fileidcache = 'fileID_cache.json'
        
        #  Google App file export translation table
        
        self._export_table = { 
                          'application/vnd.google-apps.document' : 
                          ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx'),
                          'application/vnd.google-apps.spreadsheet' : 
                          ('application/vnd.oasis.opendocument.spreadsheet', 'ods'),
                          'application/vnd.google-apps.presentation' : 
                          ('application/vnd.oasis.opendocument.presentation', 'odp')
                        }
        
        # Create local folder root
        
        if not os.path.exists(self._local_root_path):
            os.makedirs(self._local_root_path)
    
    def create_file_cache_entry(self, current_directory, file_data):
        """Create file id data dictionary entry."""
      
        # File data consists of a tuple (local file name, remote file mime type, remote file modification time)
        # A dict could by used but a tuple makes it more compact
         
        local_file = os.path.join(current_directory, file_data['name'])
         
        # File mime type incates google app file so change local file extension for export.
         
        if file_data['mimeType'] in self._export_table:
            export_tuple = self._export_table[file_data['mimeType']]
            local_file = '{}.{}'.format(os.path.splitext(local_file)[0], export_tuple[1])
     
        self._current_fileId_table[file_data['id']] = (local_file, file_data['mimeType'], file_data['modifiedTime'])
     
    def get_parents_children(self, parent_file_id):       
        """Create a list of file data for children of of given file id"""
         
        children_list = []
         
        for file_data in self._remote_drive.file_cache:
             
            if parent_file_id in file_data.get('parents', []):
                children_list.append(file_data)
                  
        return(children_list)
             
    def traverse(self, current_directory, file_list):
        """Recursively parse Google drive creating folders and file id data dictionary."""
         
        for file_data in file_list:
     
            try:
                 
                # Save away current file id data
                 
                self.create_file_cache_entry(current_directory, file_data)
                                 
                # If current file a folder then recursivelt parse
                 
                if file_data['mimeType'] == 'application/vnd.google-apps.folder':               
                    siblings_list = self.get_parents_children(file_data['id'])
                    self.traverse(os.path.join(current_directory, file_data['name']), siblings_list)
                     
            except Exception as e:
                logging.error(e)
                sys.exit(1) 
         
    def build(self):
        """Build file Id cache for remote drive."""
        
        try:
               
            # Get top level folder contents
             
            root_folder_id = self._remote_drive.file_get_metadata('root')
            top_level = self.get_parents_children(root_folder_id['id'])
             
            # Traverse remote drive file cache
             
            self.traverse(self._local_root_path, top_level)

        except Exception as e:
            logging.error(e)
            sys.exit(1) 
                
    def update_file(self, local_file, modified_time, local_timezone):
        """If Google drive file has been created or is newer than local file then update."""
     
        try:
         
            if not os.path.exists(local_file):
                return(True)
             
            # Make sure timestamp is in utc for when both are localized and compared
             
            times_stamp = os.path.getmtime(local_file)
            local_date_time = local_timezone.localize(datetime.datetime.utcfromtimestamp(times_stamp)) 
            remote_date_time = local_timezone.localize(datetime.datetime.strptime(modified_time[:-5], '%Y-%m-%dT%H:%M:%S'))
             
        except Exception as e:
            logging.error(e)
            return(False)
             
        return(remote_date_time > local_date_time)

    def download_worker(self, file_id, local_file, mime_type, sleep_delay=1):
        """Download file worker thread."""
        
        # For moment create new GDrive as http module used by underlying api is
        # not multi-thread aware and also add delay in for google 403 error if more
        # than approx 8 requests a second are made.
        #
        # TO DO: Get rid of delay and GDrive creation for each download.
        
        try: 
            drive = GDrive(self._remote_drive._credentials)
            drive.file_download(file_id, local_file, mime_type)
            time.sleep(sleep_delay)
        except Exception as e:
            print(e)
            self._download_errors += 1
            
    def update(self):
        """Update any local files if needed."""
         
        file_list = []
         
        for file_id, file_data in self._current_fileId_table.items():
     
            try:
                 
                # Create any folders needed
                 
                if file_data[1] == "application/vnd.google-apps.folder":
                    if not os.path.exists(file_data[0]):
                        os.makedirs(file_data[0])
                    continue
                 
                if self._refresh or self.update_file(file_data[0], file_data[2], self._timezone):
                     
                    # Convert(export) any google application file  otherwise just download
                           
                    if file_data[1] in self._export_table:
                        export_tuple = self._export_table[file_data[1]]
                    else:
                        export_tuple = None
                              
                    file_list.append((file_id, file_data[0], export_tuple))
                      
            except Exception as e:
                logging.error(e)
                sys.exit(1)
     
        # If worker threads > 1 then use otherwise one at a time
         
        if self._numworkers > 1:
            with ThreadPoolExecutor(max_workers=self._numworkers) as executor:
                for file_to_process in file_list:
                    future = executor.submit(self.download_worker, *file_to_process)
        else:
            
            try:
                for file_to_process in file_list:
                    self._remote_drive.file_download(*file_to_process)
            except Exception as e:
                self._download_errors += 1
 
        if self._download_errors:
            logging.info('{} errors during file downloads.'.format(self._download_errors))
            self._download_errors = 0
            
    def remove_local_file(self, file_name):
        """Remove file/directory from local folder."""
         
        if os.path.isfile(file_name):
            os.unlink(file_name)
            logging.info('Deleting file {} removed/renamed/moved from My Drive'.format(file_name))
             
        elif os.path.isdir(file_name):
            os.rmdir(file_name)
            logging.info('Deleting folder {} removed/renamed/moved from My Drive'.format(file_name))
     
    def rationalise(self):
        """Clean up local folder for files removed/renamed/deleted on My Drive."""
         
        try:
             
            if os.path.exists(self.fileidcache):
                 
                with open(self.fileidcache, 'r') as json_file:
                    old_fileId_table = json.load(json_file)
                     
                for fileId in old_fileId_table:            
                    if ((fileId not in self._current_fileId_table) or 
                        (self._current_fileId_table[fileId][0] != old_fileId_table[fileId][0])):
                        remove_local_file(old_fileId_table[fileId][0])
             
        except Exception as e:
            logging.error(e)
                                
        with open(self.fileidcache, 'w') as json_file:
            json.dump(self._current_fileId_table, json_file, indent=2)
             
        self._current_fileId_table.clear()
    
    # Properties
        
    @property
    def refresh(self):
        return(self._refresh)
    
    @refresh.setter
    def refresh(self, refresh):
        self._refresh = refresh
    
    @property
    def timezone(self):
        return(self._timezone)
    
    @timezone.setter
    def timezone(self, timezone):
        self._timezone = pytz.timezone(timezone)
    
    @property
    def numworkers(self):
        return(self._numworkers)
    
    @numworkers.setter
    def numworkers(self, numworkers):
        self._numworkers = numworkers
    
    @property
    def fieldidcache(selfs):
        return(self._fieldidcache)
    
    @fieldidcache.setter
    def set_fieldidcache(self, fieldidcache):
        self._fileidcache = fieldidcache
