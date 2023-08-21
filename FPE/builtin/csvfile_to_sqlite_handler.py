""" Built-in watcher file handlers.
"""

import os
import logging
import csv
import sqlite3
import pathlib

from builtin.common import sql
from core.constants import CONFIG_SOURCE, CONFIG_EXITONFAILURE, \
    CONFIG_DELETESOURCE, CONFIG_RECURSIVE
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.handler import Handler
from core.error import FPEError


class CSVFileToSQLiteHandlerError(FPEError):
    """An error occurred in the CSVFileToSQLite handler.
    """

    def __init__(self, message) -> None:
        """CSVFileToSQLite handler error.

        Args:
            message (str): Exception message.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "CSVFileToSQLiteHandler Error: " + self.message


class CSVFileToSQLiteHandler(IHandler):
    """Import CSV file to SQLite database.

    Read in CSV file and insert/update rows within a given SQLite database/table.
    If no key attribute is specified then the rows are inserted otherwise
    updated.

    Attributes:
        handler_name : Name of handler object
        source:        Folder to watch for files
        recursive:     Boolean == true perform recursive file watch
        delete_source: Boolean == true delete source file on success
        database_file: SQLite database file name
        table_name:    SQLite table name
        key_name:      Table column key used in updates

    """

    def __init__(self, handler_config: ConfigDict) -> None:
        """Initialise handler attributes.   

        Args:
            handler_config (ConfigDict): Handler configuration.

        Raises:
           CSVFileToSQLiteHandlerError: None passed as handler configuration.
        """

        if handler_config is None:
            raise CSVFileToSQLiteHandlerError("None passed as handler config.")

        self.source = handler_config[CONFIG_SOURCE]
        self.exitonfailure = handler_config[CONFIG_EXITONFAILURE]
        self.recursive = handler_config[CONFIG_RECURSIVE]
        self.delete_source = handler_config[CONFIG_DELETESOURCE]

        self.table_name = handler_config["table"]
        self.key_name = handler_config["key"]
        self.database_file = handler_config["databasefile"]

        self.param_style = "named"

        Handler.setup_path(handler_config, CONFIG_SOURCE)

    def process(self, source_path: pathlib.Path) -> bool:
        """Import CSV file to SQLite database.
        """

        success: bool = True

        try:

            if not os.path.exists(self.database_file):
                raise IOError("Database file does not exist.")

            database = sqlite3.connect(self.database_file)

            cursor = database.cursor()

            logging.info("Importing CSV file %s to table %s.",
                         source_path, self.table_name)

            with open(source_path, "r", encoding="utf-8") as file_handle:

                csv_reader = csv.DictReader(file_handle)

                sql_query = sql.generate(self.param_style, self.table_name,
                                         self.key_name,
                                         csv_reader.fieldnames)

                for csv_row in csv_reader:
                    cursor.execute(sql_query, csv_row)

        except (IOError, sqlite3.Error, sqlite3.Warning) as error:
            if self.exitonfailure:
                raise CSVFileToSQLiteHandlerError(error) from error
            else:
                logging.info(CSVFileToSQLiteHandlerError(error.msg))
            database = None
            success = False

        finally:
            logging.info("Finished Importing file %s to table %s.",
                         source_path, self.table_name)

            if database:
                database.commit()
                database.close()

        return success
