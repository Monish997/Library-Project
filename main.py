import sys
from app import MainWindow
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication

if __name__ == "__main__":
    font = QFont("Calibri", 11)
    app = QApplication(sys.argv)
    app.setFont(font)
    mainWindow = MainWindow()
    sys.exit(app.exec_())