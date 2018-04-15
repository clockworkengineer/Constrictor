import os
import sys
import time
import ConfigParser
import filehandlers
import logging
from watchdog.observers import Observer
from _dbus_bindings import Dictionary


def get_handler_config_section(config, section_name):
    
    handler_section = {}
    handler_options = config.options(section_name)
    
    for option in handler_options:
        
        try:
            handler_section[option] = config.get(section_name, option)
                
        except Exception as e:
            logging.error('Error on option {}.\n{}'.format(option, e))
            handler_section[option] = None
            
    handler_section['name'] = section_name
        
    return handler_section


def load_config(config_filename):
    
    # Read in config file
    
    config = ConfigParser.ConfigParser()
    config.read(config_filename)
    
    logging_params = {}
    logging_params['level'] = logging.INFO
    logging_params['format'] = '%(asctime)s:%(module)s:%(message)s'
    
    try :
        
        if 'General' in config.sections():
            section = get_handler_config_section(config, 'General')
            if 'logfile' in section:
                logging_params['filename'] = section['logfile']
            if 'loglevel' in section:
                logging_params['level'] = section['level']
            if 'logformat' in section:
                logging_params['format'] = section['logformat']
                
            config.remove_section('General')
            
    except Exception as e:
        logging.error(e)
    
    finally:   
        logging.basicConfig(**logging_params)
        return(config)


def main(config_filename):
    
    # Load config
    
    config = load_config(config_filename)
        
    logging.info('File Processing Engine Started.')

    observers_list = []
    
    for handler_name in config.sections():
         
        try:
                        
            handler_section = get_handler_config_section(config, handler_name)
            file_handler = filehandlers.create_file_handler(handler_section)
                                
        except Exception as e:
            logging.error(e)
            
        else:
            if file_handler != None:
                observer = Observer()
                observer.schedule(file_handler, file_handler.watch_folder, recursive=True) 
                observer.start()
                observers_list.append(observer)
        
    try:      
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        for observer in observers_list:
            observer.stop()
            
    finally:
        for observer in observers_list:   
            observer.join()


if __name__ == '__main__':
    if (len(sys.argv) == 2) and os.path.exists(sys.argv[1]):
        main(sys.argv[1])
    else:
        print('Error: Either no or non-existant config file passed to FPE.')
