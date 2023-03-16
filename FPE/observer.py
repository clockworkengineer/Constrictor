"""File Observer handling code.
"""

import time
import logging

from watchdog.observers import Observer
from factory import create_event_handler


def create_observer(handler_config):
    """Create file handler attach to an observer and start watching."""

    try:

        # Default values for optional field

        if not 'recursive' in handler_config:
            handler_config['recursive'] = False
        if not 'deletesource' in handler_config:
            handler_config['deletesource'] = True

        file_handler = create_event_handler(handler_config)

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
