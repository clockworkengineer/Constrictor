"""File Observer handling code.
"""

import time
import logging

from watchdog.observers import Observer
from config import load_config, get_config_section
from factory import create_event_handler


def create_observer(config, handler_name):
    """Create file handler attach to an observer and start watching."""

    try:

        # Default values for optional fields

        handler_section = {'recursive': False,
                           'deletesource': True}

        # Merge config with default values and create handler

        handler_section.update(get_config_section(config, handler_name))
        file_handler = create_event_handler(handler_section)

    except Exception as e:
        logging.error(e)
        observer = None

    else:
        # Create observer with file handler and start watching

        if file_handler is not None:
            observer = Observer()
            observer.schedule(file_handler, file_handler.watch_folder,
                              recursive=file_handler.recursive)
            observer.start()
        else:
            observer = None

    return observer


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
