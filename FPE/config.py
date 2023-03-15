""" Config handling code.
"""

import sys
import configparser
import json
import logging


def get_config_section(config, section_name):
    """Get configuration file section and return dictionary for it"""

    config_section = {}

    for option in config.options(section_name):

        try:
            config_section[option] = config.get(section_name, option)

            # Automatically set any boolean values (don't use getBoolean)
            if config_section[option] in ('True', 'False'):
                config_section[option] = config_section[option] == 'True'

        except Exception as e:
            logging.error('Error on option {}.\n{}'.format(option, e))
            config_section[option] = None

    # Save away section name for use

    config_section['name'] = section_name

    return config_section


def load_config(arguments):
    """Load configuration file and set logging parameters"""

    try:

        # Read in config file

        with open(arguments.file) as json_file:
            config = json.load(json_file)
      
        if not 'handlers' in config:
            raise ValueError("Missing config handlers key'.")
        if not 'watchers' in config:
            raise ValueError("Missing config watchers key'.")
        
        # Default logging parameters

        logging_params = {'level': logging.INFO,
                          'format': '%(asctime)s:%(message)s'}

        # Read in any logging options, merge with default and
        # remove logging section

        if 'Logging' in config:
            logging_params.update(get_config_section(config, 'Logging'))
            # If level passed in then convert to int.
            if logging_params['level'] is not int:
                logging_params['level'] = int(logging_params['level'])
            logging_params.pop('name')
            config.pop('Logging')

        logging.basicConfig(**logging_params)  # Set logging options



    except Exception as e:
        logging.error(e)
        sys.exit(1)

    return config
