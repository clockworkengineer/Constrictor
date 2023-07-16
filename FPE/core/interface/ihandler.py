"""FPE File handler interface.

Protocol class that defines the file handler interface.

"""

import pathlib
from typing import Protocol

from core.config import ConfigDict


class IHandler(Protocol):
    """Interface for watcher file handler.
    """

    handler_config: ConfigDict  # Handler config dictionary
    __source : str
    __destination : str
    __exitonfailure: bool

    def process(self, source_path: pathlib.Path) -> bool:
        """Perform watcher file processing.

        Args:
            source_path (pathlib.Path): Source fiel path.
        """
        ...
        
    @property
    def source(self) -> str:
        return self.__source
    
    @property
    def destination(self) -> str:
        return self.__destination
    
    @property
    def exitonfailure(self) -> bool:
        return self.__exitonfailure
    
    
        
    
