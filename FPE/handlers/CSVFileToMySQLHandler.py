"""Import CSV file to MySQL file hander."""

from common import _display_details, _update_row
import MySQLdb
import csv
import logging
import os
from watchdog.events import FileSystemEventHandler

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class CSVFileToMySQLHandler(FileSystemEventHandler):
    """Convert CSV file to MySQL table event handler.
    
    Read in CSV file and insert/update rows within a given MySQL database/table.
    If no key attribute is specified then the rows are inserted otherwise 
    updated.
    
    Attributes:
    hanlder_name : Name of handler object
    watch_folder:  Folder to watch for files
    server:        MySQL database server
    user:          MySQL user name
    password:      MySQL user password
    database_name: MySQL database name
    table_name:    MySQL table name
    key:           Table column key used in updates
    recursive:     Boolean that if true means perform recursive file watch   
    """
    
    def __init__(self, handler_section):
        """ Intialise handler attributes and log details."""
               
        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.server = handler_section['server']
        self.user_name = handler_section['user']
        self.user_password = handler_section['password']
        self.database_name = handler_section['database']
        self.table_name = handler_section['table']
        self.key_name = handler_section['key']
        self.recursive = handler_section['recursive']
        
        _display_details(handler_section)
        
    def on_created(self, event):
        """Import CSV file to MySQL database."""
        
        try:
            
            database = None        
            database = MySQLdb.connect(self.server, self.user_name,
                                 self.user_password, self.database_name)          
            cursor = database.cursor()
    
            logging.info ('Imorting CSV file {} to table {}.'.
                          format(event.src_path, self.table_name))
    
            with open(event.src_path, 'r') as file_handle:
                
                csv_reader = csv.DictReader(file_handle)
                           
                for row in csv_reader:
         
                    try:
                        sql = _update_row(self.table_name, self.key_name, row)
                        cursor.execute(sql)
                        database.commit()
                        
                    except (MySQLdb.Error, MySQLdb.Warning) as e:
                        logging.error ('{}\n{}'.format(sql, e))
                        database.rollback()
                        
        except Exception as e:  
            logging.error("Error in handler {}: {}".
                          format(self.handler_name, e))
        
        else:
            logging.info ('Finished Imorting file {} to table {}.'.
                          format(event.src_path, self.table_name))
            os.remove(event.src_path)
            
        finally:
            if database:
                database.close()
