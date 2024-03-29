""" FPE CSV file to SQLite built-in handler.
"""

import logging
import csv
import sqlite3
import pathlib

from builtin.common import sql
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.handler import Handler
from core.error import FPEError


class CSVFileToSQLiteHandlerError(FPEError):
    """An error occurred in the CSVFileToSQLite handler."""

    def __str__(self) -> str:
        return "CSVFileToSQLiteHandler Error: " + str(self.error)


class CSVFileToSQLiteHandler(IHandler):
    """Import CSV file to SQLite database.

    Read in CSV file and insert/update rows within a given SQLite database/table.
    If no key attribute is specified then the rows are inserted otherwise
    updated.

    Attributes:
        name:            Name of handler object
        source:          Folder to watch for files
        delete_source:   Boolean == true delete source file on success
        exit_on_failure: Boolean == true exit handler on failure; generating an exception
        recursive:       Boolean == true recursively generate events in source tree
        database_file:   SQLite database file name
        table_name:      SQLite table name
        key_name:        Table column key used in updates

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

        Handler.set_mandatory_config(self, handler_config)

        self.table_name: str  = handler_config["table"]
        self.key_name: str  = handler_config["key"]
        self.database_file: str  = handler_config["databasefile"]

    def process(self, source_path: pathlib.Path) -> bool:
        """Import CSV file to SQLite database."""

        try:
            if not pathlib.Path(self.database_file).exists():
                raise IOError("Database file does not exist.")

            database = sqlite3.connect(self.database_file)

            cursor = database.cursor()

            logging.info(
                "Importing CSV file %s to table %s.", source_path, self.table_name
            )

            with open(source_path, "r", encoding="utf-8") as file_handle:
                csv_reader = csv.DictReader(file_handle)

                sql_query = sql.generate(
                    ":{}", self.table_name, self.key_name, csv_reader.fieldnames
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

        except (IOError, sqlite3.Error, sqlite3.Warning) as error:
            self.errors += 1
            logging.info(CSVFileToSQLiteHandlerError(str(error)))

        return False

    def status(self) -> str:
        """Return current handler status string

        Returns:
            str: Handler status string.
        """

        return Handler.status(self)
