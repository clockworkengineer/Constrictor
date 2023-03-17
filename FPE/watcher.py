""" File watcher class.
"""

from watchdog.events import FileSystemEventHandler


class Watcher(FileSystemEventHandler):
    ...