# Form implementation generated from reading ui file 'c:\Projects\Constrictor\FPE\ui\QtMainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_fpe_main_window(object):
    def setupUi(self, fpe_main_window):
        fpe_main_window.setObjectName("fpe_main_window")
        fpe_main_window.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=fpe_main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.running_watchers_groupbox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.running_watchers_groupbox.setGeometry(QtCore.QRect(10, 10, 276, 231))
        self.running_watchers_groupbox.setObjectName("running_watchers_groupbox")
        self.gridLayout = QtWidgets.QGridLayout(self.running_watchers_groupbox)
        self.gridLayout.setObjectName("gridLayout")
        self.fpe_running_watchers_list = QtWidgets.QListWidget(parent=self.running_watchers_groupbox)
        self.fpe_running_watchers_list.setObjectName("fpe_running_watchers_list")
        self.gridLayout.addWidget(self.fpe_running_watchers_list, 0, 0, 1, 1)
        fpe_main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=fpe_main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        fpe_main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=fpe_main_window)
        self.statusbar.setObjectName("statusbar")
        fpe_main_window.setStatusBar(self.statusbar)

        self.retranslateUi(fpe_main_window)
        QtCore.QMetaObject.connectSlotsByName(fpe_main_window)

    def retranslateUi(self, fpe_main_window):
        _translate = QtCore.QCoreApplication.translate
        fpe_main_window.setWindowTitle(_translate("fpe_main_window", "File Processing Engine"))
        self.running_watchers_groupbox.setTitle(_translate("fpe_main_window", "Running Watchers"))
