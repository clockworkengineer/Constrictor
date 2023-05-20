
import logging
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

from core.engine import Engine

def fpe_windowed(fpe_engine: Engine):
    logging.info("Running with a user interface.")
    qapp = QApplication(sys.argv)
    fpe_gui = MainWindow(fpe_engine)
    fpe_gui.show()
    sys.exit(qapp.exec())     