"""FPE Plugin interface.
"""


class IPlugin:
    """Plugin interface.
    """

    def register(self) -> None:
        """Register the necessary items in the watcher handler factory.
        """
        ...
