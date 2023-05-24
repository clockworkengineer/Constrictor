
from PyQt6.QtWidgets import QMainWindow
import json

from ui.QtMainWindow_ui import Ui_fpe_main_window
from core.engine import Engine

from core.constants import CONFIG_WATCHERS


class MainWindow(QMainWindow, Ui_fpe_main_window):
    """Main user interface window.
    """

    def rowChanged(self, row: int) -> None:
        self.fpe_watcher_config_textedit.setPlainText(json.dumps(
            self.fpe_engine.running_config()[CONFIG_WATCHERS][row], indent=1))

    def start(self) -> None:
        current: int = self.fpe_running_watchers_list.currentIndex().row()
        watcher = self.fpe_running_watchers_list.currentItem().text()
        if self.fpe_running_watcher_stop_button.text() == "Start":
            self.fpe_running_watcher_stop_button.setText("Stop")
            self.fpe_engine.start_watcher(watcher)
        else:
            self.fpe_running_watcher_stop_button.setText("Start")
            self.fpe_engine.stop_watcher(watcher)

    def __init__(self, fpe_engine: Engine, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.fpe_engine = fpe_engine

        self.fpe_running_watchers_list.addItems(
            fpe_engine.running_watchers_list())

        self.fpe_running_watchers_list.setCurrentRow(0)
        self.rowChanged(0)

        self.fpe_running_watchers_list.currentRowChanged.connect(
            self.rowChanged)

        self.fpe_running_watcher_stop_button.clicked.connect(self.start)
