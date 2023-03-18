"""Import CSV file to MySQL file handler."""


import mysql
import csv
import logging
import os
from handler_common import generate_sql


class CSVFileToMySQL:
    """Import CSV file to MySQL database.

    Read in CSV file and insert/update rows within a given MySQL database/table.
    If no key attribute is specified then the rows are inserted otherwise
    updated.

    Attributes:
        handler_name : Name of handler object
        watch_folder:  Folder to watch for files
        server:        MySQL database server
        user_name:     MySQL user name
        user_password: MySQL user password
        database_name: MySQL database name
        table_name:    MySQL table name
        key_name:      Table column key used in updates
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
        self.param_style = 'pyformat'

    def on_created(self, event):
        """Import CSV file to MySQL database."""

        try:

            database = mysql.connect(self.server, self.user_name,
                                     self.user_password, self.database_name)
            cursor = database.cursor()

            logging.info('Imorting CSV file {} to table {}.'.
                         format(event.src_path, self.table_name))

            with open(event.src_path, 'r') as file_handle:

                csv_reader = csv.DictReader(file_handle)
                sql = generate_sql(self.param_style, self.table_name, self.key_name,
                                   csv_reader.fieldnames)

                for row in csv_reader:

                    try:

                        with database:
                            cursor.execute(sql, row)

                    except (mysql.Error, mysql.Warning) as e:
                        logging.error('{}\n{}'.format(sql, e))

        except Exception as e:
            logging.error("Error in handler {}: {}".
                          format(self.handler_name, e))
            database = None

        else:
            logging.info('Finished Imorting file {} to table {}.'.
                         format(event.src_path, self.table_name))
            if self.delete_source:
                os.remove(event.src_path)

        if database:
            database.close()
