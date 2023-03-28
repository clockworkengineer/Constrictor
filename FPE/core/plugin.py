"""Plugin Interface and loader.
"""

import importlib


class IPlugin:
    """Represents a plugin interface. A plugin has a single register function.
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
        """Load plugins names passed in.
        """

        plugin: IPlugin
        for plugin_file in plugin_list:
            plugin = importlib.import_module(plugin_file)
            plugin.register()
