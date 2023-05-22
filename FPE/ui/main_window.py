from PyQt6.QtWidgets import QMainWindow

from ui.QtMainWindow_ui import Ui_fpe_main_window
from core.engine import Engine


class MainWindow(QMainWindow, Ui_fpe_main_window):
    """Main user interface window.
    """

    def __init__(self, fpe_engine: Engine, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.fpe_engine = fpe_engine

        self.fpe_running_watchers_list.addItems(
            fpe_engine.running_watchers_list())
