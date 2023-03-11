""" Config handling code.
"""

import sys
import configparser
import logging


__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def get_config_section(config, section_name):
    """Get configuration file section and return dictionary for it"""

    config_section = {}

    for option in config.options(section_name):

        try:
            config_section[option] = config.get(section_name, option)

            # Automatically set any boolean values (dont use getBoolean)
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

        config = configparser.ConfigParser()
        config.read(arguments.file)

        # Default logging parameters

        logging_params = {'level': logging.INFO,
                          'format': '%(asctime)s:%(message)s'}

        # Read in any logging options, merge with default and
        # remove logging section

        if 'Logging' in config.sections():
            logging_params.update(get_config_section(config, 'Logging'))
            # If level passed in then convert to int.
            if logging_params['level'] is not int:
                logging_params['level'] = int(logging_params['level'])
            logging_params.pop('name')
            config.remove_section('Logging')

        logging.basicConfig(**logging_params)  # Set logging options

        # If handler name set then remove all others from config
        # leaving the config empty if the handler doesn't exist

        if arguments.name is not None:

            if not config.has_section(arguments.name):
                logging.info('Error: Non-existant file handler {}.'.
                             format(arguments.name))

            for section in config.sections():
                if section != arguments.name:
                    config.remove_section(section)

    except Exception as e:
        logging.error(e)
        sys.exit(1)

    return config
