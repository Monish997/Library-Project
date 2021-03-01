import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app.widgets import Dashboard
from app import cursor
from app.dialogs import ScanQR


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.cursor = cursor

        self.setWindowIcon(QIcon("images/icon.ico"))
        self.resize(1280, 720)
        self.setCentralWidget(Dashboard(self))
        self.show()
        self.handleLogin()

    def switchFunc(self, WidgetClass):
        self.setCentralWidget(WidgetClass(self))

    def dashboardFunc(self):
        self.setCentralWidget(Dashboard(self))
        self.centralWidget().changePermissions(self.staffQR)

    def logoutFunc(self):
        self.setCentralWidget(Dashboard(self))
        self.handleLogin()

    def handleLogin(self):
        self.staffQR = ScanQR(
            self,
            sql="SELECT staff_id FROM staff WHERE staff_id='{}';",
            prompt="Scan QR code in staff ID to login",
        ).exec_()
        if self.staffQR:
            self.centralWidget().changePermissions(self.staffQR)
        else:
            sys.exit(0)
