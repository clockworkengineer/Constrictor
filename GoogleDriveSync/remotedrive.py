"""Class for accessing remote drive.

This is a child class of GDevice that caches the remote  Google drive contents
for performance and reduce the number of http requests,
"""

import logging

from gdrive import GDrive

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class RemoteDrive(GDrive):
    """Class to access remote drive.
    
    Access remote drive files (keeping a complete file cache locally).
    
    Attrubutes:
        _file_translator   File translator object
        file_cache:        Drive file cache.
        root_folder_id:    File ID for root folder.
    """

    def __init__(self, credentials, file_translator):
        
        try:
            
            super().__init__(credentials)

            self._file_translator = file_translator

            self.root_folder_id = self.file_get_metadata('root').get('id', None)

        except Exception as e:
            logging.error(e)
            
    def refresh_file_cache(self):
        """Refresh remote drive file cache."""
        
        try:

            self.file_cache = self.file_list(query='not trashed',
                                             file_fields=
                                             'name, id, parents, mimeType, modifiedTime')

        except Exception as e:
            logging.error(e)
    
    # Properties
     
    @property
    def file_cache(self):
        return self._file_cache
    
    @file_cache.setter
    def file_cache(self, file_cache):
        self._file_cache = file_cache
        
    @property
    def root_folder_id(self):
        return self._root_folder_id
    
    @root_folder_id.setter
    def root_folder_id(self, root_folder_id):
        self._root_folder_id = root_folder_id
