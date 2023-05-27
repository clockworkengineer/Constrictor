
from PyQt6.QtWidgets import QMainWindow
import json

from ui.QtMainWindow_ui import Ui_fpe_main_window
from core.engine import Engine

from core.constants import CONFIG_WATCHERS


class MainWindow(QMainWindow, Ui_fpe_main_window):
    """Main user interface window.
    """

    def __set_start_stop_button_title(self, watcher_name: str) -> None:
        """_summary_

        Args:
            watcher_name (str): _description_
        """

        if self.fpe_engine.is_watcher_running(watcher_name):
            self.fpe_running_watcher_start_stop_button.setText("Stop")
        else:
            self.fpe_running_watcher_start_stop_button.setText("Start")

    def __rowChanged(self, row: int) -> None:
        """_summary_

        Args:
            row (int): _description_
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
        """_summary_
        """

        watcher_name = self.fpe_running_watchers_list.currentItem().text()
        if not self.fpe_engine.is_watcher_running(watcher_name):
            self.fpe_engine.start_watcher(watcher_name)
        else:
            self.fpe_engine.stop_watcher(watcher_name)
        self.__set_start_stop_button_title(watcher_name)

    def _delete_watcher(self) -> None:
        """_summary_
        """

        watcher_name = self.fpe_running_watchers_list.currentItem().text()
        self.fpe_engine.delete_watcher(watcher_name)
        self.fpe_running_watchers_list.takeItem(
            self.fpe_running_watchers_list.currentRow())

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

        self.fpe_running_watchers_list.setCurrentRow(0)
        self.__rowChanged(0)

        self.fpe_running_watchers_list.currentRowChanged.connect(
            self.__rowChanged)

        self.fpe_running_watcher_start_stop_button.clicked.connect(
            self.__start_stop_watcher)

        self.fpe_watcher_config_textedit.setReadOnly(True)

        self.fpe_running_watcher_delete_button.clicked.connect(
            self._delete_watcher)
