""" Handler class.
"""

from typing import Protocol


class Handler(Protocol):
    def process(self):
        ...
