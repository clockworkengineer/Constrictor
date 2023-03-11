"""Create file event handler object.
  
Factory function create_event_handler used to create a file handler object
from the handler config section passed in. These handlers are then passed into 
a watchdog observer specially created for it and used to process files passed
to handler method on_created().

"""

import logging
import handlers


def create_event_handler(handler_section):
    """Generate watchdog event handler object for the configuration section passed in."""

    file_handler = None

    try:

        handler_class = getattr(handlers, handler_section['type'])
        file_handler = handler_class(handler_section)

    except KeyError as e:
        logging.error("Missing option {}.\n{} not started.".format(
            e, handler_section['name']))
    except AttributeError:
        logging.error('Invalid file handler type [{type}].\n{name} not started.'.format(
            **handler_section))

    return file_handler