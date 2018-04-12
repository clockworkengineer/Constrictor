import os
import time
import ConfigParser
import filehandlers

from watchdog.observers import Observer


def get_handler_config_section(config, section_name):
    
    handler_section = {}
    handler_options = config.options(section_name)
    
    for option in handler_options:
        
        try:
            handler_section[option] = config.get(section_name, option)
                
        except Exception as e:
            print('Error on option {}.'.format(option))
            print(e)
            handler_section[option] = None
            
    handler_section['name'] = section_name
        
    return handler_section

    
if __name__ == "__main__":
    
    print ('Python File Processing Engine')

    config = ConfigParser.ConfigParser()
    config.read('/home/robt/config/PFPE.conf')
    
    observers_list = []
    
    for handler_name in config.sections():
         
        try:
            handler_section = get_handler_config_section(config, handler_name)
            file_handler = filehandlers.create_file_handler(handler_section)
                         
        except KeyError as e:
            print("{} error in key {}".format(handler_name, e))
            
        except Exception as e:
            print(e)
            
        else:
            if file_handler != None:
                observer = Observer()
                observer.schedule(file_handler, handler_section['watch'], recursive=True) 
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
