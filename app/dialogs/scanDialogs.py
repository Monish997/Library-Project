from app import cursor
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class InputDialog(QDialog):
    def __init__(self, parent, title, prompt, regex, sql, errorTitle, errorMessage) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.setupUi(title, prompt, regex)
        self.sql, self.errorTitle, self.errorMessage = sql, errorTitle, errorMessage
        self.connectUi()

    def setupUi(self, title, prompt, regex):
        self.setWindowTitle(title)
        self.resize(400, 150)

        self.gridLayout = QGridLayout(self)

        self.inputLabel = QLabel(prompt, self)
        self.gridLayout.addWidget(self.inputLabel, 0, 0, 1, 1)

        self.inputLineEdit = QLineEdit(self)
        self.inputLineEdit.setValidator(QRegExpValidator(regex))
        self.gridLayout.addWidget(self.inputLineEdit, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

    def connectUi(self):
        self.inputLineEdit.returnPressed.connect(self.acceptFunc)
        self.buttonBox.accepted.connect(self.acceptFunc)
        self.buttonBox.rejected.connect(self.reject)

    def acceptFunc(self):
        sequence = self.inputLineEdit.text()
        self.cursor.execute(self.sql.format(sequence))
        _ = self.cursor.fetchall()
        if self.cursor.rowcount > 0:
            self.accept()
        else:
            QMessageBox.warning(self, self.errorTitle, self.errorMessage)

    def exec_(self):
        if super().exec_():
            return self.inputLineEdit.text()
        return 0


class ScanQR(InputDialog):
    def __init__(self, parent, sql, prompt) -> None:
        super().__init__(
            parent,
            "Scan QR",
            prompt,
            "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
            sql,
            "Invalid QR Code",
            "Please scan a valid QR code",
        )


class ScanISBN13(InputDialog):
    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            "Scan ISBN-13",
            "Scan ISBN-13 of the book",
            "^[0-9]{13}$",
            "SELECT isbn_13 FROM books WHERE isbn_13 = '{}';",
            "Invalid ISBN-13",
            "Please scan a valid ISBN-13 barcode",
        )