from PyQt6.QtWidgets import QMainWindow
from ui.QtMainWindow_ui import Ui_MainWindow

from core.engine import Engine


class MainWindow(QMainWindow, Ui_MainWindow):
    """_summary_

    Args:
        QMainWindow (_type_): _description_
        Ui_MainWindow (_type_): _description_
    """
    def __init__(self, fpe_engine: Engine, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.fpe_engine = fpe_engine
