"""File Event Handlers.

File event handler classes and support functions. Uses CreateFileEventHandler  
factory function to create an event handler object from the handler config 
section passed in. These handlers are then passed into a watchdog observer
specically created for it and used to process files passed to handler method
on_created().

Current built in file handlers:
1) Copy files/directory
2) Import CSV file to MySQL database table.
3) Import CSV file to SQLite database table.
"""

import handlers
import logging

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def CreateFileEventHandler(handler_section):
    """Generate watchdog event handler object for the configuration section passed in."""
    
    file_handler = None;
    
    try:

        handler_class = getattr(handlers, handler_section['type'])
        file_handler = handler_class(handler_section)
        
    except KeyError as e:
        logging.error("Missing option {}.\n{} not started.".format(e, handler_section['name']))
    except Exception as e:
        print(e)
        logging.error('Invalid file handler type [{type}].\n{name} not started.'.format(**handler_section))

    return (file_handler)

