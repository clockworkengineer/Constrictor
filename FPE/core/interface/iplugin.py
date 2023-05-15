"""Plugin interface.
"""


class IPlugin:
    """Plugin interface.
    """

    @staticmethod
    def register() -> None:
        """Register the necessary items in the watcher handler factory.
        """
