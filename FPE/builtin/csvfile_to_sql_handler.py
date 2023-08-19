""" Built-in watcher file handlers.
"""

import os
import logging
import csv
import pathlib
import mysql.connector


from core.constants import CONFIG_NAME, CONFIG_SOURCE, CONFIG_EXITONFAILURE, \
    CONFIG_DELETESOURCE, CONFIG_RECURSIVE
from core.interface.ihandler import IHandler
from core.config import ConfigDict
from core.handler import Handler
from core.error import FPEError


################################
# Common handler functionality #
################################


def generate_sql(param_style, table_name, key_name, row_fields) -> str:
    """Generate SQL for update/insert row of fields.
    """

    sql: str = ""

    try:

        # Set up placeholder for param_style supported

        if param_style == "pyformat":
            placeholder = "%({})s"
        elif param_style == "named":
            placeholder = ":{}"
        else:
            logging.error("Unsupported paramstyle %s.", param_style)
            placeholder = ""

        # Key provided then doing update

        if key_name != "":

            fields = (("{} = " + placeholder + ",") *
                      len(row_fields)).format(*sorted(row_fields + row_fields))[:-1]

            sql = ("UPDATE {} SET {} WHERE {} = " + placeholder).format(table_name,
                                                                        fields, key_name, key_name)
        # Doing an insert of a new record

        else:

            fields = ""
            for field in row_fields:
                fields += "`"
                fields += field
                fields += "`,"

            fields = fields[:-1]

            values = ((placeholder + ",") *
                      (len(row_fields))).format(*row_fields)[:-1]

            sql = f"INSERT INTO `{table_name}` ({fields}) VALUES ({values})"

    except ValueError as error:
        logging.error(error)
        sql = None

    logging.debug(sql)

    return sql


class CSVFileToSQLHandlerError(FPEError):
    """An error occurred in the CSVFileToSQL handler.
    """

    def __init__(self, message) -> None:
        """CSVFileToSQL handler error.

        Args:
            message (str): Exception message.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "CSVFileToSQLHandler Error: " + self.message


class CSVFileToSQLHandler(IHandler):
    """Import CSV file to MySQL database.

    Read in CSV file and insert/update rows within a given MySQL database/table.
    If no key attribute is specified then the rows are inserted otherwise
    updated.

    Attributes:
        name :         Name of handler object
        source:        Directory to watch for files
        recursive:     Boolean == true perform recursive file watch
        delete_source: Boolean == true delete source file on success
        server:        MySQL database server
        user_name:     MySQL username
        user_password: MySQL user password
        database_name: MySQL database name
        table_name:    MySQL table name
        key_name:      Table column key used in updates

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

        self.name = handler_config[CONFIG_NAME]
        self.source = handler_config[CONFIG_SOURCE]
        self.exitonfailure = handler_config[CONFIG_EXITONFAILURE]
        self.recursive = handler_config[CONFIG_RECURSIVE]
        self.delete_source = handler_config[CONFIG_DELETESOURCE]

        self.server = Handler.get_config(handler_config, "server")
        self.port = Handler.get_config(handler_config, "port")
        self.user_name = Handler.get_config(handler_config, "user")
        self.user_password = Handler.get_config(handler_config, "password")
        self.database_name = Handler.get_config(handler_config, "database")
        self.table_name = Handler.get_config(handler_config, "table")
        self.key_name = Handler.get_config(handler_config, "key")

        self.param_style = "pyformat"

        Handler.setup_path(handler_config, CONFIG_SOURCE)

    def process(self, source_path: pathlib.Path) -> bool:
        """Import CSV file to SQLite database.
        """

        success: bool = True

        try:

            database = mysql.connector.connect(host=self.server,
                                               port=self.port,
                                               user=self.user_name,
                                               passwd=self.user_password,
                                               database=self.database_name)

            cursor = database.cursor()

            logging.info("Importing CSV file %s to table %s.",
                         source_path, self.table_name)

            with open(source_path, "r", encoding="utf-8") as file_handle:

                csv_reader = csv.DictReader(file_handle)

                sql = generate_sql(self.param_style, self.table_name, self.key_name,
                                   csv_reader.fieldnames)

                for csv_row in csv_reader:
                    cursor.execute(sql, csv_row)

        except mysql.connector.Error as error:
            if self.exitonfailure:
                raise CSVFileToSQLHandlerError(error) from error
            else:
                logging.info(CSVFileToSQLHandlerError(error.msg))
            database = None
            success = False

        finally:
            logging.info("Finished Importing file %s to table %s.",
                         source_path, self.table_name)

            if database:
                database.commit()
                database.close()

        return success
