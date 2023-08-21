"""  Generate SQL query string.
"""

import logging


def generate(param_style, table_name, key_name, row_fields) -> str:
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

            sql = f"UPDATE {table_name} SET {fields} WHERE {key_name} =" + \
                placeholder.format(key_name)

        # Doing an insert of a new record

        else:

            fields = ",".join(row_fields)

            values = ((placeholder + ",") *
                      (len(row_fields))).format(*row_fields)[:-1]

            sql = f"INSERT INTO `{table_name}` ({fields}) VALUES ({values})"

    except ValueError as error:
        logging.error(error)
        sql = ""

    logging.debug(sql)

    return sql
