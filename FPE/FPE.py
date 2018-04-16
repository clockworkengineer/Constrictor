#!/usr/bin/env python

"""File Processing Engine.

This is a generic file processing engine that sets up a watch folder and waits 
for files/directories to be copied to it. Any added directories are also watched 
(if recursive is set) but any added files are be processed using one of its built 
in file handler classes.
"""

from FPE import file_handlers
import os
import sys
import time
import ConfigParser
import logging
from watchdog.observers import Observer

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Alpha"


def get_config_section(config, section_name):
    """Get configutation file section and return dictionary for it"""
    
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


def load_config(config_filename):
    """Load configuration file and set general run parameters"""
    
    # Read in config file
    
    config = ConfigParser.ConfigParser()
    config.read(config_filename)
    
    # Default logging parameters
    
    logging_params = {}
    logging_params['level'] = logging.INFO
    logging_params['format'] = '%(asctime)s:%(module)s:%(message)s'

    # Read in any logging options, merge with default and remove logging section
    
    try :
        
        if 'Logging' in config.sections():
            logging_params.update(get_config_section(config, 'Logging'))
            logging_params.pop('name')
            config.remove_section('Logging')
            
    except Exception as e:
        logging.error(e)
    
    finally:   
        logging.basicConfig(**logging_params)
        return(config)


def main(config_filename):
    """Main program entry point"""
    
    # Load config
    
    config = load_config(config_filename)
        
    logging.info('File Processing Engine Started.')

    observers_list = []

    # Loop through sections creating file handlers and starting observers for them
        
    for handler_name in config.sections():
         
        try:
            
            # Default values for optional fields
            
            handler_section = { 'recursive' : False}
            
            # Merge config with default values and create handler
            
            handler_section.update(get_config_section(config, handler_name))
            file_handler = file_handlers.create_file_handler(handler_section)
                                
        except Exception as e:
            logging.error(e)
            
        else:
            # Create observer for file handler, startup and add to observers list
            if file_handler != None:
                observer = Observer();
                observer.schedule(file_handler, file_handler.watch_folder, recursive=file_handler.recursive) 
                observer.start()
                observers_list.append(observer)
    
    # Currently run observers until quit
       
    try:      
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Stop all observers
        for observer in observers_list:
            observer.stop()
            
    finally:
        # Wait for all observer threads to stop
        for observer in observers_list:   
            observer.join()

#####################################################################
# Start up main program/check for confiuration file being passed in #
#####################################################################


if __name__ == '__main__':
    if (len(sys.argv) == 2) and os.path.exists(sys.argv[1]):
        main(sys.argv[1])
    else:
        print('Error: Either no or non-existant config file passed to FPE.')
