"""FPE Qt based windows UI.
"""

import json
from PyQt6.QtWidgets import QDialog

from ui.QtWatcherInfoDialog_ui import Ui_QtWatcherInfoDialog
from core.config import ConfigDict
from core.engine import Engine
from core.constants import CONFIG_WATCHERS, CONFIG_NAME


class WatcherInfoDialog(QDialog, Ui_QtWatcherInfoDialog):
    """_summary_

    Args:
        QDialog (_type_): _description_
        Ui_QtWatcherInfoDialog (_type_): _description_
    """

    __watcher_config: ConfigDict
    __fpe_engine: Engine

    def __handle_refresh(self) -> None:
        """_summary_"""
        self.watcher_info_config_textedit.setPlainText(
            json.dumps(self.__watcher_config, indent=1)
        )
        self.watcher_info_status_textedit.setPlainText(
            self.__fpe_engine.return_watcher(
                self.__watcher_config[CONFIG_NAME]
            ).status
        )

    def __init__(self, row: int, fpe_engine: Engine, parent=None) -> None:
        """_summary_

        Args:
            row (int): _description_
            fpe_engine (Engine): _description_
            parent (_type_, optional): _description_. Defaults to None.
        """
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Watcher Info")

        self.__watcher_config = fpe_engine.running_config[CONFIG_WATCHERS][row]
        self.__fpe_engine = fpe_engine

        self.setWindowTitle("Watcher Info (" + self.__watcher_config["name"] + ")")

        self.watcher_info_refresh_button.clicked.connect(self.__handle_refresh)

        self.__handle_refresh()
