"""Run FPE with windowed UI.
"""

import logging
import sys
from PyQt6.QtWidgets import QApplication
from ui.fpe_main_window import MainWindow

from core.engine import Engine


def fpe_windowed(fpe_engine: Engine) -> None:
    """Run FPE in QTMainWindow.

    Args:
        fpe_engine (Engine): FPE control engine.
    """
    
    logging.info("Running with a user interface.")
    qt_app = QApplication(sys.argv)
    fpe_gui = MainWindow(fpe_engine)
    fpe_gui.show()
    qt_app.exec()
