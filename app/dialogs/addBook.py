from uuid import uuid4

import qrcode
from app import cursor
from app.utils import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class AddBook(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.setupUi()
        self.connectUi()

    def setupUi(self):
        self.setWindowTitle("Add Book")
        self.resize(720, 360)
        self.setModal(True)

        self.gridLayout = QGridLayout(self)

        self.titleLabel = QLabel("Title", self)
        self.gridLayout.addWidget(self.titleLabel, 0, 0, 1, 1)

        self.titleLineEdit = QLineEdit(self)
        self.gridLayout.addWidget(self.titleLineEdit, 0, 1, 1, 1)

        self.isbn13Label = QLabel("ISBN 13", self)
        self.gridLayout.addWidget(self.isbn13Label, 1, 0, 1, 1)

        self.isbn13LineEdit = QLineEdit(self)
        self.isbn13LineEdit.setValidator(QRegExpValidator("^[0-9]{13}$"))
        self.gridLayout.addWidget(self.isbn13LineEdit, 1, 1, 1, 1)

        self.categoryLabel = QLabel("Category", self)
        self.gridLayout.addWidget(self.categoryLabel, 2, 0, 1, 1)

        self.categoryComboBox = QuickComboBox("SELECT category_name FROM categories", parent=self)
        self.gridLayout.addWidget(self.categoryComboBox, 2, 1, 1, 1)

        self.numberOfCopiesLabel = QLabel("Number of Copies", self)
        self.gridLayout.addWidget(self.numberOfCopiesLabel, 3, 0, 1, 1)

        self.numberOfCopiesSpinBox = QSpinBox(self)
        self.gridLayout.addWidget(self.numberOfCopiesSpinBox, 3, 1, 1, 1)

        self.authorLabel = QLabel("Author", self)
        self.gridLayout.addWidget(self.authorLabel, 4, 0, 1, 1)

        self.authorComboBox = QuickComboBox(
            "SELECT author_name from authors;",
            parent=self,
        )
        self.gridLayout.addWidget(self.authorComboBox, 4, 1, 1, 1)

        self.publisherLabel = QLabel("Publisher", self)
        self.gridLayout.addWidget(self.publisherLabel, 5, 0, 1, 1)

        self.publisherComboBox = QuickComboBox(
            "SELECT publisher_name FROM publishers;", parent=self
        )
        self.gridLayout.addWidget(self.publisherComboBox, 5, 1, 1, 1)

        self.datePublishedLabel = QLabel("Date Published", self)
        self.gridLayout.addWidget(self.datePublishedLabel, 6, 0, 1, 1)

        self.datePublishedDateEdit = QuickDateEdit(self)
        self.datePublishedDateEdit.setDate(QDate.currentDate())
        self.gridLayout.addWidget(self.datePublishedDateEdit, 6, 1, 1, 1)

        self.priceLabel = QLabel("Price", self)
        self.gridLayout.addWidget(self.priceLabel, 7, 0, 1, 1)

        self.priceLineEdit = QLineEdit(self)
        self.priceLineEdit.setValidator(QIntValidator())
        self.gridLayout.addWidget(self.priceLineEdit, 7, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)

        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)

    def connectUi(self):
        self.buttonBox.accepted.connect(self.addBookFunc)
        self.buttonBox.rejected.connect(self.reject)

    def addBookFunc(self):
        title = self.titleLineEdit.text().strip()
        category = self.categoryComboBox.currentText()
        isbn13 = self.isbn13LineEdit.text()
        price = self.priceLineEdit.text()
        copies = self.numberOfCopiesSpinBox.value()
        author = self.authorComboBox.currentText()
        publisher = self.publisherComboBox.currentText()
        datePublished = str(self.datePublishedDateEdit.date().toPython())
        if not title:
            QMessageBox.warning(self, "Insufficient Data", "Please fill the title.")
            return
        if len(isbn13) < 13:
            QMessageBox.warning(
                self, "Incorrect ISBN-13", "Please enter correct ISBN-13 to add book."
            )
            return
        if not price:
            QMessageBox.warning(self, "Insufficient Data", "Please enter price to add book.")
            return
        else:
            price = int(price)

        folderName = QFileDialog.getExistingDirectory(self, "Save QR codes to")
        if folderName:
            record = (isbn13, title, category, author, publisher, datePublished, price)
            self.cursor.execute(f"INSERT INTO books VALUES {record};")

            dateAcquired = str(QDate.currentDate().toPython())

            for i in range(1, copies + 1):
                uuid = str(uuid4())
                self.cursor.execute(
                    f"INSERT INTO copies VALUES ('{uuid}', '{isbn13}', '{dateAcquired}');"
                )
                qrcode.make(uuid).save(f"{folderName}/{title} Copy {i}.png")
            self.accept()
        else:
            QMessageBox.warning(self, "Book not Added", "Please save copy qr codes to add book.")
            return
