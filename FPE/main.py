import os
import sys
import time
import ConfigParser
import filehandlers
import logging
from watchdog.observers import Observer


def get_config_section(config, section_name):
    """Get configutation file section and return dictionary for it"""
    
    config_section = {}
    
    for option in config.options(section_name):
        
        try:
            config_section[option] = config.get(section_name, option)
                
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
        # Set logging parameters and return config
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
                        
            handler_section = get_config_section(config, handler_name)
            file_handler = filehandlers.create_file_handler(handler_section)
                                
        except Exception as e:
            logging.error(e)
            
        else:
            # Create observer for file handler, startup and add to observers list
            if file_handler != None:
                observer = Observer()
                observer.schedule(file_handler, file_handler.watch_folder, recursive=True) 
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


if __name__ == '__main__':
    if (len(sys.argv) == 2) and os.path.exists(sys.argv[1]):
        main(sys.argv[1])
    else:
        print('Error: Either no or non-existant config file passed to FPE.')
