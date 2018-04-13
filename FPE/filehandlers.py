import os
import shutil
from watchdog.events import FileSystemEventHandler
import csv
import MySQLdb


def _display_details(handler_section):
    print ('\n{} Handler [{}] running...'.format(handler_section['name'], handler_section['type']))
    for option in handler_section.keys():
        if option != 'name' and option != 'type':
            print('{} = {}'.format(option, handler_section[option]))


def create_file_handler(handler_section):
    
    file_handler = None;

    try:
        if handler_section['type'] == CopyFileHandler.__name__:
            file_handler = CopyFileHandler(handler_section)
        elif handler_section['type'] == CSVFileToMySQLHandler.__name__:
            file_handler = CSVFileToMySQLHandler(handler_section)
        else:
            print ('\nInvalid file handler type {}.\n{} not started.'.format(handler_section['type'], handler_section['name']))
    
    except KeyError as e:
        print("\nMissing option {}.\n{} not started.".format(e, handler_section['name']))
    
    return (file_handler)

    
class CopyFileHandler(FileSystemEventHandler):
    
    def __init__(self, handler_section):

        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.destination_folder = handler_section['destination']
        
        _display_details(handler_section)
         
    def on_created(self, event):
        
        try:
            
            destination_path = event.src_path[len(self.watch_folder) + 1:]    
            destination_path = os.path.join(self.destination_folder, destination_path)
                    
            if os.path.isfile(event.src_path):            
                if not os.path.exists(os.path.dirname(destination_path)):
                    os.makedirs(os.path.dirname(destination_path))
                print ('Copying file {} to {}'.format(event.src_path, destination_path))
                shutil.copy2(event.src_path, destination_path)
                
            elif os.path.isdir(event.src_path):           
                if not os.path.exists(destination_path):
                    print ('Creating directory {}'.format(event.src_path))
                    os.makedirs(destination_path)    

        except Exception as e:
            print("Error in handler {}: {}".format(self.handler_name, e))

 
class CSVFileToMySQLHandler(FileSystemEventHandler):
    
    def __init__(self, handler_section):
        
        self.handler_name = handler_section['name']
        self.watch_folder = handler_section['watch']
        self.server = handler_section['server']
        self.user_name = handler_section['user']
        self.user_password = handler_section['password']
        self.database_name = handler_section['database']
        self.table_name = handler_section['table']
        self.key_name = handler_section['key']

        _display_details(handler_section)

    @staticmethod
    def __insert_row(table_name, row):
            
        fields = ''
        values = ''
        for field in row.keys():
            fields += '{},'.format(field)
            values += '\'{}\','.format(row[field].replace("'", "''"))
 
        fields = fields[:-1]
        values = values[:-1]
     
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, fields, values)
        
        print(sql)
            
        return (sql)

    @staticmethod
    def __update_row(table_name, key, row):
          
        fields = ''     
        for field in row.keys():
            fields += '{} = \'{}\','.format(field, row[field].replace("'", "''"))
            
        fields = fields[:-1]
        
        sql = 'UPDATE {} SET {} WHERE {} = {}'.format(table_name, fields, key, row[key])
        
        print(sql)
        
        return (sql)
        
    def on_created(self, event):
        
        try:
            
            db = MySQLdb.connect(self.server, self.user_name, self.user_password, self.database_name)
            
            cursor = db.cursor()
    
            print ('Imorting CSV file {}'.format(event.src_path))
    
            with open(event.src_path, 'r') as file_handle:
                
                csv_reader = csv.DictReader(file_handle)
                           
                for row in csv_reader:
         
                    try:
                        if self.key_name != '':
                            sql = self.__update_row(self.table_name, self.key_name, row)
                        else:
                            sql = self.__insert_row(self.table_name, row)
    
                        cursor.execute(sql)
                        db.commit()
                        
                    except (MySQLdb.Error, MySQLdb.Warning) as e:
                        print (sql)
                        print(e)
                        db.rollback()
                        
            os.remove(event.src_path)
                        
        except Exception as e:  
            print("Error in handler {}: {}".format(self.handler_name, e))
        
        finally:     
            db.close()
