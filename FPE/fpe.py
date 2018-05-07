#!/usr/bin/env python3

"""File Processing Engine.

This is a generic file processing engine that sets up a watch folder and waits 
for files/directories to be copied to it. Any added directories are also watched 
(if recursive is set) but any added files are be processed using one of its built 
in file handler classes.

Current built in file handlers:
1) Copy files/directory
2) Import CSV file to MySQL database table.
3) Import CSV file to SQLite database table.
4) SFTP copy files/directory to an SSH server.

usage: fpe.py [-h] [-n NAME] file

Process files copied into watch folder with a custom handler.

positional arguments:
  file                  Configration file

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  File handler name
"""

from handlerfactory import CreateFileEventHandler 
import sys
import os
import time
import configparser
import logging
import argparse
from watchdog.observers import Observer

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
        
        logging_params = { 'level' : logging.INFO,
                           'format' : '%(asctime)s:%(message)s' }
    
        # Read in any logging options, merge with default and 
        # remove logging section
             
        if 'Logging' in config.sections():
            logging_params.update(get_config_section(config, 'Logging'))
            # If level passed in then convert to int.
            if  logging_params['level'] is not int:
                logging_params['level'] = int(logging_params['level'])
            logging_params.pop('name')
            config.remove_section('Logging')
            
        logging.basicConfig(**logging_params)  # Set logging options
               
        # If handler name set then remove all others from config
        # leaving the config empty if the handler doesn't exist
        
        if arguments.name != None:
            
            if not config.has_section(arguments.name):
                logging.info('Error: Non-existant file handler {}.'.
                             format(arguments.name))
                
            for section in config.sections():
                if section != arguments.name:
                    config.remove_section(section)
    
    except Exception as e:
        logging.error(e)
        sys.exit(1)
     
    return(config)

    
def load_arguments():
    """Load and parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Process files copied into watch folder with a custom handler.')
    parser.add_argument('file', help='Configration file')
    parser.add_argument('-n', '--name', help="File handler name")
    
    arguments = parser.parse_args()
    
    if not os.path.exists(arguments.file):
        print('Error: Non-existant config file passed to FPE.')
        sys.exit(1)

    return(arguments)


def create_observer(config, handler_name):
    """Create file handler attach to an observer and start watching."""
    
    try:
        
        # Default values for optional fields
        
        handler_section = {'recursive' : False,
                           'deletesource' : True }
        
        # Merge config with default values and create handler
        
        handler_section.update(get_config_section(config, handler_name))
        file_handler = CreateFileEventHandler(handler_section)
                        
    except Exception as e:
        logging.error(e)
        
    else:
        # Create observer with file handler and start watching
        
        if file_handler != None:
            observer = Observer();
            observer.schedule(file_handler, file_handler.watch_folder,
                              recursive=file_handler.recursive) 
            observer.start()
        else:
            observer = None;
            
    return(observer)


def observe_folders(observers_list):
    """Run observers until user quits (eg.Control-C)"""
    
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
    
########################
# FPE Main Entry Point #
########################


def Main():
    """Main program entry point"""

    arguments = load_arguments()
 
    config = load_config(arguments)
                
    logging.info('File Processing Engine Started.')

    observers_list = []

    # Loop through config sections creating file observers
        
    for handler_name in config.sections():
                
        observer = create_observer(config, handler_name)
        if observer != None:
            observers_list.append(observer)
    
    # If list not empty observer folders
          
    if observers_list:          
        observe_folders(observers_list)

    else:
        logging.error('Error: No file handlers configured.')
   
    logging.info('File Processing Engine Stopped.')   


if __name__ == '__main__':
    Main()
