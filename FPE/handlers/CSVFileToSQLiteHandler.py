from common import _display_details, _update_row
import csv
import logging
import os
import sqlite3
from watchdog.events import FileSystemEventHandler

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class CSVFileToSQLiteHandler(FileSystemEventHandler):
    """Import CSV file to SQLite database.
 
    Read in CSV file and insert/update rows within a given SQLite database/table.
    If no key attribute is specified then the rows are inserted otherwise 
    updated.
    
    Attributes:
    hanlder_name : Name of handler object
    watch_folder:  Folder to watch for files
    database_file: SQLite database file name
    table_name:    SQLite table name
    key:           Table column key used in updates
    recursive:     Boolean that if true means perform recursive file watch          
    """
    
    def __init__(self, handler_section):
        """ Intialise handler attributes and log details"""
        
        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.table_name = handler_section['table']
        self.key_name = handler_section['key']
        self.database_file = handler_section['databasefile']
        self.recursive = handler_section['recursive']
        
        _display_details(handler_section)

    def on_created(self, event):
        """Import CSV file to SQLite database."""
                
        try:
            
            database = None
        
            if not os.path.exists(self.database_file):
                raise IOError("Database file does not exist.")
            
            database = sqlite3.connect(self.database_file)
            
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
                         
                    except (sqlite3.Error, sqlite3.Warning) as e:
                        logging.error('{}\n{}'.format(sql, e))
                        database.rollback()
                        
        except (Exception) as e:  
            logging.error("Error in handler {}: {}".
                          format(self.handler_name, e))
        
        else:
            logging.info ('Finished Imorting file {} to table {}.'.
                          format(event.src_path, self.table_name))
            os.remove(event.src_path)
            
        finally:
            if database:
                database.close()

