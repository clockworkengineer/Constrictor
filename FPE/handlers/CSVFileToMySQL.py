"""Import CSV file to MySQL file hander."""

from common import _display_details, _generate_sql
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


class CSVFileToMySQL(FileSystemEventHandler):
    """Import CSV file to MySQL database.
    
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
    recursive:     Boolea == true perform recursive file watch  
    delete_source: Boolean == true delete source file on sucess  
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
        self.delete_source = handler_section['deletesource']
        self.field_format = ':{}'
                
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
                sql = _generate_sql('%({})s', self.table_name, self.key_name,
                                    csv_reader.fieldnames)
                           
                for row in csv_reader:

                    try:

                        with database:
                            cursor.execute(sql, row)
                        
                    except (MySQLdb.Error, MySQLdb.Warning) as e:
                        logging.error ('{}\n{}'.format(sql, e))
                        
        except Exception as e:  
            logging.error("Error in handler {}: {}".
                          format(self.handler_name, e))
        
        else:
            logging.info ('Finished Imorting file {} to table {}.'.
                          format(event.src_path, self.table_name))
            if self.delete_source:
                os.remove(event.src_path)
            
        finally:
            if database:
                database.close()
