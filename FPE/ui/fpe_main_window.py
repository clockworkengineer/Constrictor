"""FPE Qt based windows UI.
"""

import json
from PyQt6.QtWidgets import QMainWindow

from ui.QtMainWindow_ui import Ui_fpe_main_window
from core.engine import Engine

from core.constants import CONFIG_WATCHERS


class MainWindow(QMainWindow, Ui_fpe_main_window):
    """Main user interface window.
    """

    def __set_start_stop_button_title(self, watcher_name: str) -> None:
        """Set Start/Stop button depending on watchers running state.

        Args:
            watcher_name (str): Watcher name.
        """

        if self.fpe_engine.is_watcher_running(watcher_name):
            self.fpe_running_watcher_start_stop_button.setText("Stop")
        else:
            self.fpe_running_watcher_start_stop_button.setText("Start")

    def __row_changed(self, row: int) -> None:
        """Set UI for watcher selected from list.

        Args:
            row (int): Row of currently selected watcher.
        """

        if row != -1:
            self.fpe_watcher_config_textedit.setPlainText(json.dumps(
                self.fpe_engine.running_config()[CONFIG_WATCHERS][row], indent=1))
            self.__set_start_stop_button_title(
                watcher_name=self.fpe_running_watchers_list.currentItem().text())
        else:
            self.fpe_watcher_config_textedit.setPlainText("")
            self.fpe_running_watcher_start_stop_button.setEnabled(False)
            self.fpe_running_watcher_delete_button.setEnabled(False)

    def __start_stop_watcher(self) -> None:
        """Start/Stop watcher.
        """

        watcher_name = self.fpe_running_watchers_list.currentItem().text()
        if not self.fpe_engine.is_watcher_running(watcher_name):
            self.fpe_engine.start_watcher(watcher_name)
        else:
            self.fpe_engine.stop_watcher(watcher_name)
        self.__set_start_stop_button_title(watcher_name)

    def __delete_watcher(self) -> None:
        """Delete watcher from engine running list.
        """

        watcher_name = self.fpe_running_watchers_list.currentItem().text()
        self.fpe_running_watchers_list.takeItem(
            self.fpe_running_watchers_list.currentRow())
        self.fpe_engine.delete_watcher(watcher_name)

    def __init__(self, fpe_engine: Engine, parent=None):
        """Main FPE UI window.

        Args:
            fpe_engine (Engine): FPE Engine.
            parent (QtWidget, optional): FPE Window parent. Defaults to None.
        """

        super().__init__(parent)
        self.setupUi(self)

        self.fpe_engine = fpe_engine

        self.fpe_running_watchers_list.currentRowChanged.connect(
            self.__row_changed)

        self.fpe_running_watcher_start_stop_button.clicked.connect(
            self.__start_stop_watcher)

        self.fpe_running_watcher_delete_button.clicked.connect(
            self.__delete_watcher)

        self.fpe_running_watcher_save_button.clicked.connect(
            self.fpe_engine.save_config)

        self.fpe_watcher_config_textedit.setReadOnly(True)

        self.fpe_running_watchers_list.addItems(
            fpe_engine.running_watchers_list())

        self.fpe_running_watchers_list.setCurrentRow(0)
