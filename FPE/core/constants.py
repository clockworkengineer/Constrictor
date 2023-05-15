from typing import Final, Tuple

CONFIG_SOURCE: Final[str] = "source"
CONFIG_DESTINATION: Final[str] = "destination"
CONFIG_NAME: Final[str] = "name"
CONFIG_TYPE: Final[str] = "type"
CONFIG_WATCHERS: Final[str] = "watchers"
CONFIG_PLUGINS: Final[str] = "plugins"
CONFIG_DELETESOURCE: Final[str] = "deletesoure"
CONFIG_EXITONFAILURE: Final[str] = "exitonfailure"

CONFIG_MANDATORY_KEYS: Final[Tuple[str, ...]] = (
    CONFIG_PLUGINS, CONFIG_WATCHERS)
CONFIG_WATCHER_MANDATORY_KEYS: Final[Tuple[str, ...]] = (
    CONFIG_NAME, CONFIG_TYPE, CONFIG_SOURCE)
