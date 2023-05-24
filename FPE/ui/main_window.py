
from PyQt6.QtWidgets import QMainWindow
import json

from ui.QtMainWindow_ui import Ui_fpe_main_window
from core.engine import Engine


class MainWindow(QMainWindow, Ui_fpe_main_window):
    """Main user interface window.
    """

    def rowChanged(self, row):
        self.fpe_watcher_config_textedit.setPlainText(json.dumps(
            self.fpe_engine.running_config()["watchers"][row], indent=1))

    def __init__(self, fpe_engine: Engine, parent=None):
        """_summary_

        Args:
            fpe_engine (Engine): _description_
            parent (_type_, optional): _description_. Defaults to None.
        """

        super().__init__(parent)
        self.setupUi(self)
        self.fpe_engine = fpe_engine

        self.fpe_running_watchers_list.addItems(
            fpe_engine.running_watchers_list())

        self.rowChanged(0)

        self.fpe_running_watchers_list.currentRowChanged.connect(
            self.rowChanged)
