""" Watcher file handler definitons built-in.
"""

import os
import shutil
import logging
from typing import Protocol
# import csv
# import sqlite3
# import pysftp
# import mysql


class Handler(Protocol):
    """Watcher file handler class"""

    def process(self, event):
        """Perform watcher file processing."""

################################
# Common handler fcuntionality #
################################


def generate_sql(param_tyle, table_name, key_name, row_fields):
    """Generate SQL for update/insert row of fields."""

    try:

        # Set up placeholder for paramstyle supported

        if param_tyle == "pyformat":
            placeholder = "%({})s"
        elif param_tyle == "named":
            placeholder = ":{}"
        else:
            logging.error(
                f"Unsupported paramstyle {param_tyle}".format(param_tyle))
            placeholder = ""

        fields = ""

        # Key provided then doing update

        if key_name != "":

            fields = (("{} = " + placeholder + ",") *
                      len(row_fields)).format(*sorted(row_fields + row_fields))[:-1]

            sql = ("UPDATE {} SET {} WHERE {} = " + placeholder).format(table_name,
                                                                        fields, key_name, key_name)
        # Doing an insert of a new record

        else:

            fields = ",".join(row_fields)
            values = ((placeholder + ",") *
                      (len(row_fields))).format(*row_fields)[:-1]

            sql = f"INSERT INTO {table_name} ({fields}) VALUES ({values})"

    except ValueError as error:
        logging.error(error)
        sql = None

    logging.debug(sql)

    return sql

#####################
# Built in handlers #
#####################


class CopyFile(Handler):
    """Copy file/directories.

    Copy files created in watch folder to destination folder keeping any in 
    situ watch folder directory structure the same.

    Attributes:
        handler_name:         Name of handler object
        watch_folder:         Folder to watch for files
        destination_folder:   Destination for file copy
        recursive:            Boolean == true perform recursive file watch
        delete_source:        Boolean == true delete source file on success
    """

    def __init__(self, handler_section):
        """ Initialise handler attributes and log details."""

        self.handler_name = handler_section["name"]
        self.watch_folder = handler_section["watch"]
        self.destination_folder = handler_section["destination"]
        self.recursive = handler_section["recursive"]
        self.delete_source = handler_section["deletesource"]

    def process(self, event):
        """Copy file from watch folder to destination."""
        try:

            destination_path = event.src_path[len(self.watch_folder) + 1:]
            destination_path = os.path.join(self.destination_folder,
                                            destination_path)

            if os.path.isfile(event.src_path):
                if not os.path.exists(os.path.dirname(destination_path)):
                    os.makedirs(os.path.dirname(destination_path))
                logging.info(
                    f"Copying file {event.src_path} to {destination_path}")
                shutil.copy2(event.src_path, destination_path)

            elif os.path.isdir(event.src_path):
                if not os.path.exists(destination_path):
                    logging.info("Creating directory {event.src_path}")
                    os.makedirs(destination_path)

            if self.delete_source:
                os.remove(event.src_path)
    
        except Exception as error:
            logging.error(f"Error in handler {self.handler_name} : {error}")


# class CSVFileToMySQL(Handler):
#     """Import CSV file to MySQL database.

#     Read in CSV file and insert/update rows within a given MySQL database/table.
#     If no key attribute is specified then the rows are inserted otherwise
#     updated.

#     Attributes:
#         handler_name : Name of handler object
#         watch_folder:  Folder to watch for files
#         server:        MySQL database server
#         user_name:     MySQL user name
#         user_password: MySQL user password
#         database_name: MySQL database name
#         table_name:    MySQL table name
#         key_name:      Table column key used in updates
#         recursive:     Boolea == true perform recursive file watch
#         delete_source: Boolean == true delete source file on sucess
#     """

#     def __init__(self, handler_section):
#         """ Intialise handler attributes and log details."""

#         self.handler_name = handler_section["name"]
#         self.watch_folder = handler_section["watch"]
#         self.server = handler_section["server"]
#         self.user_name = handler_section["user"]
#         self.user_password = handler_section["password"]
#         self.database_name = handler_section["database"]
#         self.table_name = handler_section["table"]
#         self.key_name = handler_section["key"]
#         self.recursive = handler_section["recursive"]
#         self.delete_source = handler_section["deletesource"]
#         self.param_style = "pyformat"

#     def process(self, event):
#         """Import CSV file to MySQL database."""

#         try:

#             database = mysql.connect(self.server, self.user_name,
#                                      self.user_password, self.database_name)
#             cursor = database.cursor()

#             logging.info("Imorting CSV file {} to table {}.".
#                          format(event.src_path, self.table_name))

#             with open(event.src_path, "r") as file_handle:

#                 csv_reader = csv.DictReader(file_handle)
#                 sql = generate_sql(self.param_style, self.table_name, self.key_name,
#                                    csv_reader.fieldnames)

#                 for row in csv_reader:

#                     try:

#                         with database:
#                             cursor.execute(sql, row)

#                     except (mysql.Error, mysql.Warning) as e:
#                         logging.error("{}\n{}".format(sql, e))

#         except Exception as e:
#             logging.error("Error in handler {}: {}".
#                           format(self.handler_name, e))
#             database = None

#         else:
#             logging.info("Finished Imorting file {} to table {}.".
#                          format(event.src_path, self.table_name))
#             if self.delete_source:
#                 os.remove(event.src_path)

#         if database:
#             database.close()


# class CSVFileToSQLite(Handler):
#     """Import CSV file to SQLite database.

#     Read in CSV file and insert/update rows within a given SQLite database/table.
#     If no key attribute is specified then the rows are inserted otherwise
#     updated.

#     Attributes:
#         handler_name : Name of handler object
#         watch_folder:  Folder to watch for files
#         database_file: SQLite database file name
#         table_name:    SQLite table name
#         key_name:      Table column key used in updates
#         recursive:     Boolea == true perform recursive file watch
#         delete_source: Boolean == true delete source file on sucess
#     """

#     def __init__(self, handler_section):
#         """ Intialise handler attributes and log details"""

#         self.handler_name = handler_section["name"]
#         self.watch_folder = handler_section["watch"]
#         self.table_name = handler_section["table"]
#         self.key_name = handler_section["key"]
#         self.database_file = handler_section["databasefile"]
#         self.recursive = handler_section["recursive"]
#         self.delete_source = handler_section["deletesource"]
#         self.param_style = "named"

#     def process(self, event):
#         """Import CSV file to SQLite database."""

#         try:

#             database = None

#             if not os.path.exists(self.database_file):
#                 raise IOError("Database file does not exist.")

#             database = sqlite3.connect(self.database_file)

#             cursor = database.cursor()

#             logging.info("Imorting CSV file {} to table {}.".
#                          format(event.src_path, self.table_name))

#             with open(event.src_path, "r") as file_handle:

#                 csv_reader = csv.DictReader(file_handle)
#                 sql = generate_sql(self.param_style, self.table_name,
#                                    self.key_name,
#                                    csv_reader.fieldnames)

#                 for row in csv_reader:

#                     try:

#                         with database:
#                             cursor.execute(sql, row)

#                     except (sqlite3.Error, sqlite3.Warning) as e:
#                         logging.error("{}\n{}".format(sql, e))

#         except Exception as e:
#             logging.error("Error in handler {}: {}".
#                           format(self.handler_name, e))
#             database = None

#         else:
#             logging.info("Finished Imorting file {} to table {}.".
#                          format(event.src_path, self.table_name))
#             if self.delete_source:
#                 os.remove(event.src_path)

#         if database:
#             database.close()

# class SFTPCopyFile(Handler):
#     """SFTP Copy file/directories.

#     SFTP Copy files created in watch folder to destination folder on remote SSH
#     server keeping any in situ watch folder directory structure the same.

#     Attributes:
#         handler_name:  Name of handler object
#         watch_folder:  Folder to watch for files
#         ssh_server:    SSH Server
#         ssh_user:      SSH Server user name
#         ssh_password   SSH Server user password
#         destination    Destination for copy
#         recursive:     Boolean == true perform recursive file watch
#         delete_source: Boolean == true delete source file on sucess
#     """

#     def __init__(self, handler_section):
#         """ Intialise handler attributes and log details."""

#         self.handler_name = handler_section["name"]
#         self.watch_folder = handler_section["watch"]
#         self.ssh_server = handler_section["server"]
#         self.ssh_user = handler_section["user"]
#         self.ssh_password = handler_section["password"]
#         self.destination_folder = handler_section["destination"]
#         self.recursive = handler_section["recursive"]
#         self.delete_source = handler_section["deletesource"]

#         logging.getLogger("paramiko").setLevel(logging.WARNING)

#     def process(self, event):
#         """SFTP Copy file from watch folder to a destination folder on remote server."""

#         destination_path = event.src_path[len(self.watch_folder) + 1:]
#         destination_path = os.path.join(self.destination_folder,
#                                         destination_path)

#         with pysftp.Connection(self.ssh_server, username=self.ssh_user,
#                                password=self.ssh_password) as sftp:
#             if os.path.isfile(event.src_path):
#                 sftp.put(event.src_path, destination_path)
#             else:
#                 sftp.makedirs(destination_path)

#         logging.info("Uploaded file {} to {}".format(
#             event.src_path, destination_path))
#         if self.delete_source:
#             os.remove(event.src_path)
