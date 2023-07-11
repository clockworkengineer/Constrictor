"""FPE related constant definitions.
"""

from typing import Final, Tuple

APP_NAME: Final[str] = "FPE"

CONFIG_SOURCE: Final[str] = "source"
CONFIG_DESTINATION: Final[str] = "destination"
CONFIG_NAME: Final[str] = "name"
CONFIG_TYPE: Final[str] = "type"
CONFIG_WATCHERS: Final[str] = "watchers"
CONFIG_PLUGINS: Final[str] = "plugins"
CONFIG_FILENAME: Final[str] = "filename"
CONFIG_DELETESOURCE: Final[str] = "deletesource"
CONFIG_SERVER: Final[str] = "server"
CONFIG_USER: Final[str] = "user"
CONFIG_PASSWORD: Final[str] = "password"
CONFIG_NOGUI: Final[str] = "nogui"
CONFIG_RECURSIVE: Final[str] = "recursive"
CONFIG_EXITONFAILURE: Final[str] = "exitonfailure"
CONFIG_FILES_PROCESSED: Final[str] = "processed"
CONFIG_MANDATORY_KEYS: Final[Tuple[str, ...]] = (
    CONFIG_PLUGINS, CONFIG_WATCHERS)
CONFIG_WATCHER_MANDATORY_KEYS: Final[Tuple[str, ...]] = (
    CONFIG_NAME, CONFIG_TYPE, CONFIG_SOURCE)
