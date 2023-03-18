""" File watcher class.
"""

import logging
from factory import create_watcher
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class WatcherHandler(FileSystemEventHandler):
    def __init__(self, watcher_handler) -> None:
        super().__init__()
        self.watcher_handler = watcher_handler

    def on_created(self, event):
        self.watcher_handler.on_created(event)


class Watcher:

    event_handler: WatcherHandler

    def __init__(self, watcher_config) -> None:
        try:

            # Default values for optional field

            if not 'recursive' in watcher_config:
                watcher_config['recursive'] = False
            if not 'deletesource' in watcher_config:
                watcher_config['deletesource'] = True

            self.file_handler = create_watcher(watcher_config)

            self.event_handler = WatcherHandler(self.file_handler)

        except Exception as e:
            logging.error(e)
            self.observer = None

    def start(self):
        if self.file_handler is not None:
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.file_handler.watch_folder,
                                   recursive=self.file_handler.recursive)
            self.observer.start()

    def stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()
