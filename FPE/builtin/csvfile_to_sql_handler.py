""" FPE CSV file to SQL built-in handler.
"""

import logging
import csv
import pathlib
import mysql.connector

from builtin.common import sql
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.handler import Handler
from core.error import FPEError


class CSVFileToSQLHandlerError(FPEError):
    """An error occurred in the CSVFileToSQL handler."""

    def __str__(self) -> str:
        return "CSVFileToSQLHandler Error: " + str(self.error)


class CSVFileToSQLHandler(IHandler):
    """Import CSV file to MySQL database.

    Read in CSV file and insert/update rows within a given MySQL database/table.
    If no key attribute is specified then the rows are inserted otherwise
    updated.

    Attributes:
        name:            Name of handler object
        source:          Folder to watch for files
        delete_source:   Boolean == true delete source file on success
        exit_on_failure: Boolean == true exit handler on failure; generating an exception
        recursive:       Boolean == true recursively generate events in source tree
        server:          MySQL database server
        user_name:       MySQL username
        user_password:   MySQL user password
        database_name:   MySQL database name
        table_name:      MySQL table name
        key_name:        Table column key used in updates

    """

    def __init__(self, handler_config: ConfigDict) -> None:
        """Initialise handler attributes.

        Args:
            handler_config (ConfigDict): Handler configuration.

        Raises:
            CSVFileToSQLHandlerError: None passed as handler configuration.
        """

        if handler_config is None:
            raise CSVFileToSQLHandlerError("None passed as handler config.")

        Handler.set_mandatory_config(self, handler_config)

        self.server = Handler.get_config(handler_config, "server")
        self.port = Handler.get_config(handler_config, "port")
        self.user_name = Handler.get_config(handler_config, "user")
        self.user_password = Handler.get_config(handler_config, "password")
        self.database_name = Handler.get_config(handler_config, "database")
        self.table_name = Handler.get_config(handler_config, "table")
        self.key_name = Handler.get_config(handler_config, "key")

    def process(self, source_path: pathlib.Path) -> bool:
        """Import CSV file to SQLite database."""

        try:
            database = mysql.connector.connect(
                host=self.server,
                port=self.port,
                user=self.user_name,
                passwd=self.user_password,
                database=self.database_name,
            )

            cursor = database.cursor()

            logging.info(
                "Importing CSV file %s to table %s.", source_path, self.table_name
            )

            with open(source_path, "r", encoding="utf-8") as file_handle:
                csv_reader = csv.DictReader(file_handle)

                sql_query = sql.generate(
                    "%({})s",
                    self.table_name,
                    self.key_name,
                    csv_reader.fieldnames,
                )

                if sql_query != "":
                    for csv_row in csv_reader:
                        cursor.execute(sql_query, csv_row)
                        
            database.commit()
            database.close()
            
            logging.info(
                "Finished Importing file %s to table %s.", source_path, self.table_name
            )
                
            return True

        except mysql.connector.Error as error:
            self.errors += 1
            logging.info(CSVFileToSQLHandlerError(error.msg))
 
        return False

    def status(self) -> str:
        """Return current handler status string

        Returns:
            str: Handler status string.
        """

        return Handler.status(self)
