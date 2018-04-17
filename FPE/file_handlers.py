"""File Event Handlers.

File event handler classes and support functions. CreateFileEventHandler is a 
factory function to create an event handler object from the handler config 
section passed in and return it.
"""

import MySQLdb
import csv
import logging
import os
import shutil
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


def CreateFileEventHandler(handler_section):
    """Generate watchdog event handler object for the configuration section passed in."""
    
    file_handler = None;

    try:
        if handler_section['type'] == CopyFileHandler.__name__:
            file_handler = CopyFileHandler(handler_section)
        elif handler_section['type'] == CSVFileToMySQLHandler.__name__:
            file_handler = CSVFileToMySQLHandler(handler_section)
        elif handler_section['type'] == CSVFileToSQLiteHandler.__name__:
            file_handler = CSVFileToSQLiteHandler(handler_section)
        else:
            logging.error('Invalid file handler type [{type}].\n{name} not started.'.format(**handler_section))
    
    except KeyError as e:
        logging.error("Missing option {}.\n{} not started.".format(e, handler_section['name']))
    
    return (file_handler)


def _display_details(handler_section):
    """Display event handler details and paraneters."""
    
    logging.info('*' * 80)
    logging.info('{name} Handler [{type}] running...'.format(**handler_section))
    for option in handler_section.keys():
        if option != 'name' and option != 'type':
            logging.info('{} = {}'.format(option, handler_section[option]))


def _update_row(table_name, key, row):
    """Generate SQL for update/insert row of fields."""
  
    fields = ''     
   
    # Key provided then doing update
     
    if key != '':
        
        for field in row.keys():
            fields += '{} = \'{}\','.format(field,
                                            row[field].replace("'", "''"))
            
        fields = fields[:-1]
        
        sql = 'UPDATE {} SET {} WHERE {} = {}'.format(table_name,
                                                      fields, key, row[key])
    
    # Doing an insert of a new record
       
    else:  
           
        values = ''
        for field in row.keys():
            fields += '{},'.format(field)
            values += '\'{}\','.format(row[field].replace("'", "''"))
    
        fields, values = fields[:-1], values[:-1]
     
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name,
                                                       fields, values)
    
    logging.debug(sql)
    
    return (sql)

        
class CopyFileHandler(FileSystemEventHandler):
    """Copy file event handler.
    
    Copy files created in watch folder to destination folder keeping any in 
    situ watch folder directory structure the same.
    
    Attributes:
    handler_name:  Name of handler object
    watch_folder:  Folder to watch for files
    destination:   Destination for file copy
    recursive:     Boolean that if true means perform recursive file watch
    """
    
    def __init__(self, handler_section):
        """ Intialise handler attributes and log details."""
        
        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.destination_folder = handler_section['destination']
        self.recursive = handler_section['recursive']
        
        _display_details(handler_section)
         
    def on_created(self, event):
        """Copy file from watch folder to destination."""
        try:
            
            destination_path = event.src_path[len(self.watch_folder) + 1:]    
            destination_path = os.path.join(self.destination_folder,
                                            destination_path)
                    
            if os.path.isfile(event.src_path):            
                if not os.path.exists(os.path.dirname(destination_path)):
                    os.makedirs(os.path.dirname(destination_path))
                logging.info ('Copying file {} to {}'.
                              format(event.src_path, destination_path))
                shutil.copy2(event.src_path, destination_path)
                
            elif os.path.isdir(event.src_path):           
                if not os.path.exists(destination_path):
                    logging.info ('Creating directory {}'.
                                  format(event.src_path))
                    os.makedirs(destination_path)    

        except Exception as e:
            logging.error("Error in handler {}: {}".
                          format(self.handler_name, e))

 
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

