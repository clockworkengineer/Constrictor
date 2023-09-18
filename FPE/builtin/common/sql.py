"""  Generate SQL query string to insert/update a database table row.
"""

import logging


def generate(
    param_style: str, table_name: str, key_name: str, row_fields: [str]
) -> str:
    """Generate SQL for update/insert row of fields.

    Args:
        param_style (str):  Parameter substitionn style.
        table_name (str):   Database table name.
        key_name (str):     Primary key name.
        row_fields ([str]): Field name list.

    Returns:
        str: Return SQL query to insert/update a database row.
    """

    sql: str = ""

    try:
        # Key provided then doing update

        if key_name != "":
            fields = (("{} = " + param_style + ",") * len(row_fields)).format(
                *sorted(row_fields + row_fields)
            )[:-1]

            sql = (
                f"UPDATE {table_name} SET {fields} WHERE {key_name} ="
                + param_style.format(key_name)
            )

        # Doing an insert of a new record

        else:
            fields = ",".join(row_fields)

            values = ((param_style + ",") * (len(row_fields))).format(*row_fields)[:-1]

            sql = f"INSERT INTO `{table_name}` ({fields}) VALUES ({values})"

    except ValueError as error:
        logging.error(error)
        sql = ""

    logging.debug(sql)

    return sql
