"""Create file event handler object.
  
Factory function create_event_handler used to create a file handler object
from the handler config data passed in. These handlers are then passed into 
a watchdog observer specially created for it and used to process files passed
to handler method on_created().

"""

import logging
import handlers


def create_event_handler(handler_config):
    """Generate watchdog event handler object for the configuration passed in."""

    file_handler = None

    try:

        handler_class = getattr(handlers, handler_config['type'])
        file_handler = handler_class(handler_config)

    except KeyError as e:
        logging.error("Missing option {}.\n{} not started.".format(
            e, handler_config['name']))
    except AttributeError:
        logging.error('Invalid file handler type [{type}].\n{name} not started.'.format(
            **handler_config))

    return file_handler
