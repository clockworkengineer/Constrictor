"""Plugin Interface and loader.
"""

import importlib


class IPlugin:
    """Plugin interface class.
    """

    @staticmethod
    def register() -> None:
        """Register the necessary items in the watcher handler factory.
        """


class Plugin:
    """Plugin loader class.
    """

    @staticmethod
    def load(plugin_list: list[str]) -> None:
        """Load plugins list passed in.
        """

        plugin: IPlugin
        for plugin_file in plugin_list:
            plugin = importlib.import_module(plugin_file) # type: ignore
            plugin.register()
