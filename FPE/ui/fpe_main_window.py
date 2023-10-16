"""FPE Qt based windows UI.
"""

from PyQt6.QtWidgets import QMainWindow

from ui.QtMainWindow_ui import Ui_fpe_main_window
from ui.fpe_watcher_info_dialog import WatcherInfoDialog
from core.engine import Engine


class MainWindow(QMainWindow, Ui_fpe_main_window):
    """Main user interface window."""

    def __display_info_dialog(self):
        info_dialog = WatcherInfoDialog(self.current_row, self.fpe_engine, self)
        info_dialog.show()

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
            self.current_row = row
            self.__set_start_stop_button_title(
                watcher_name=self.fpe_running_watchers_list.currentItem().text()
            )
        else:
            self.fpe_running_watcher_start_stop_button.setEnabled(False)
            self.fpe_running_watcher_delete_button.setEnabled(False)

    def __start_stop_watcher(self) -> None:
        """Start/Stop watcher."""

        watcher_name = self.fpe_running_watchers_list.currentItem().text()
        if not self.fpe_engine.is_watcher_running(watcher_name):
            self.fpe_engine.start_watcher(watcher_name)
        else:
            self.fpe_engine.stop_watcher(watcher_name)
        self.__set_start_stop_button_title(watcher_name)

    def __delete_watcher(self) -> None:
        """Delete watcher from engine running list."""

        watcher_name = self.fpe_running_watchers_list.currentItem().text()
        self.fpe_running_watchers_list.takeItem(
            self.fpe_running_watchers_list.currentRow()
        )
        self.fpe_engine.delete_watcher(watcher_name)

    def __watcher_failure_callback(self, watcher_name: str) -> None:
        """_summary_

        Args:
            watcher_name (str): _description_
        """
        if self.fpe_engine.is_watcher_running(watcher_name):
            self.fpe_engine.stop_watcher(watcher_name)
            if watcher_name == self.fpe_running_watchers_list.currentItem().text():
                self.fpe_running_watcher_start_stop_button.setText("Start")

    def __init__(self, fpe_engine: Engine, parent=None) -> None:
        """Main FPE UI window.

        Args:
            fpe_engine (Engine): FPE Engine.
            parent (QtWidget, optional): FPE Window parent. Defaults to None.
        """

        super().__init__(parent)
        self.setupUi(self)

        self.fpe_engine = fpe_engine

        self.fpe_engine.set_failure_callback(self.__watcher_failure_callback)

        self.fpe_engine.startup()

        self.fpe_running_watchers_list.currentRowChanged.connect(self.__row_changed)

        self.fpe_running_watcher_start_stop_button.clicked.connect(
            self.__start_stop_watcher
        )

        self.fpe_running_watcher_delete_button.clicked.connect(self.__delete_watcher)

        self.fpe_running_watcher_info_button.clicked.connect(self.__display_info_dialog)

        self.fpe_running_watcher_save_button.clicked.connect(
            self.fpe_engine.save_config
        )

        self.fpe_running_watchers_list.addItems(fpe_engine.watchers_list)

        self.current_row = 0
        self.fpe_running_watchers_list.setCurrentRow(self.current_row)
