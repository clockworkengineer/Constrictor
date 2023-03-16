""" Config handling code.
"""

import sys
import configparser
import json
import logging


def load_config(arguments):
    """Load configuration file and set logging parameters"""

    try:

        # Read in config file

        with open(arguments.file) as json_file:
            config = json.load(json_file)

        # Check config data
        if not 'handlers' in config:
            raise ValueError("Missing config handlers key'.")
        if not 'watchers' in config:
            raise ValueError("Missing config watchers key'.")

        for handler_config in config['watchers']:
            if not 'name' in handler_config:
                raise ValueError("Missing config handler name key'.")
            if not 'type' in handler_config:
                raise ValueError("Missing config watchers type key'.")

        # Default logging parameters

        logging_params = {'level': logging.INFO,
                          'format': '%(asctime)s:%(message)s'}

        # Read in any logging options, merge with default and
        # remove logging section

        if 'logging' in config:
            logging_params.update(config['logging'])
            # If level passed in then convert to int.
            if logging_params['level'] is not int:
                logging_params['level'] = int(logging_params['level'])

        logging.basicConfig(**logging_params)  # Set logging options

    except Exception as e:
        logging.error(e)
        sys.exit(1)

    return config
