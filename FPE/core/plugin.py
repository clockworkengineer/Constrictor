"""Plugin interface and loader.
"""

import importlib

from core.error import FPEError


class IPlugin:
    """Plugin interface.
    """

    @staticmethod
    def register() -> None:
        """Register the necessary items in the watcher handler factory.
        """


class PluginLoaderError(FPEError):
    """An error occurred in the plugin loader.
    """

    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return "FPE Plugin Loader Error: " + str(self.message)


class PluginLoader:
    """Plugin loader.
    """

    @staticmethod
    def load(plugin_list: list[str]) -> None:
        """Load plugins list passed in.
        """

        if plugin_list is None or len(plugin_list) == 0:
            raise PluginLoaderError("None or empty list passed plugin loader.")

        try:
            plugin: IPlugin
            for plugin_file in plugin_list:
                plugin = importlib.import_module(plugin_file)  # type: ignore
                plugin.register()
        except ModuleNotFoundError as error:
            raise PluginLoaderError(error)
