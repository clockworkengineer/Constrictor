"""File handler common functions

Common functions used by some/all file event handler classes.
"""

import logging


def generate_sql(param_tyle, table_name, key_name, row_fields):
    """Generate SQL for update/insert row of fields."""

    try:

        # Set up placeholder for paramstyle supported

        if param_tyle == 'pyformat':
            placeholder = '%({})s'
        elif param_tyle == 'named':
            placeholder = ':{}'
        else:
            logging.error('Unsupported paramstyle {}'.format(param_tyle))
            placeholder = ''

        fields = ''

        # Key provided then doing update

        if key_name != '':

            fields = (('{} = ' + placeholder + ',') *
                      len(row_fields)).format(*sorted(row_fields + row_fields))[:-1]

            sql = ('UPDATE {} SET {} WHERE {} = ' + placeholder).format(table_name,
                                                                        fields, key_name, key_name)
        # Doing an insert of a new record

        else:

            fields = ','.join(row_fields)
            values = ((placeholder + ',') *
                      (len(row_fields))).format(*row_fields)[:-1]

            sql = 'INSERT INTO {} ({}) VALUES ({})'.format(
                table_name, fields, values)

    except Exception as e:
        logging.error(e)
        sql = None

    logging.debug(sql)

    return sql
