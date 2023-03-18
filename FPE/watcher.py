""" File watcher class.
"""

import logging
from factory import create_watcher
from watchdog.observers import Observer


class Watcher:

    def __init__(self, watcher_config) -> None:
        try:

            # Default values for optional field

            if not 'recursive' in watcher_config:
                watcher_config['recursive'] = False
            if not 'deletesource' in watcher_config:
                watcher_config['deletesource'] = True

            self.file_handler = create_watcher(watcher_config)

        except Exception as e:
            logging.error(e)
            self.observer = None

    def start(self):
        if self.file_handler is not None:
            self.observer = Observer()
            self.observer.schedule(self.file_handler, self.file_handler.watch_folder,
                                   recursive=self.file_handler.recursive)
            self.observer.start()

    def stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()
