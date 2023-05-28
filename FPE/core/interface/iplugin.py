"""FPE Plugin interface.

Protocol class that defines the handler plugin interface.

"""


class IPlugin:
    """Plugin interface.
    """

    def register(self) -> None:
        """Register the necessary items in the watcher handler factory.
        """
        ...
