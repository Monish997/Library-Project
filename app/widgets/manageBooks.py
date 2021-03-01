from uuid import uuid4

import qrcode
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app.dialogs import AddBook, ScanQR, ScanISBN13
from app.utils import *
from app import cursor


class ManageBooks(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.setupUi(parent)
        self.connectUi(parent)
        self.lastSQL = "SELECT 0 FROM dual WHERE false;"

    def setupUi(self, parent):
        parent.setWindowTitle("Manage Books")

        self.verticalLayout = QVBoxLayout(self)

        self.backHorizontalLayout = QHBoxLayout()

        self.back = QPushButton("Back", self)
        self.backHorizontalLayout.addWidget(self.back)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.backHorizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.backHorizontalLayout)

        self.searchGroupBox = QGroupBox(self)
        self.searchGroupBox.setTitle("Search")

        self.gridLayout = QGridLayout(self.searchGroupBox)

        self.titleLabel = QLabel("Name", self.searchGroupBox)
        self.gridLayout.addWidget(self.titleLabel, 0, 0, 1, 1)

        self.titleLineEdit = QLineEdit(self.searchGroupBox)
        self.gridLayout.addWidget(self.titleLineEdit, 0, 1, 1, 1)

        self.categoryLabel = QLabel("Category", self.searchGroupBox)
        self.gridLayout.addWidget(self.categoryLabel, 1, 0, 1, 1)

        self.categoryComboBox = QuickComboBox(
            "SELECT category_name FROM categories;",
            null=True,
            parent=self.searchGroupBox,
        )
        self.gridLayout.addWidget(self.categoryComboBox, 1, 1, 1, 1)

        self.authorLabel = QLabel("Author", self.searchGroupBox)
        self.gridLayout.addWidget(self.authorLabel, 2, 0, 1, 1)

        self.authorLineEdit = QLineEdit(self.searchGroupBox)
        self.gridLayout.addWidget(self.authorLineEdit, 2, 1, 1, 1)

        self.publisherLabel = QLabel("Publisher", self.searchGroupBox)
        self.gridLayout.addWidget(self.publisherLabel, 3, 0, 1, 1)

        self.publisherLineEdit = QLineEdit(self.searchGroupBox)
        self.gridLayout.addWidget(self.publisherLineEdit, 3, 1, 1, 1)

        self.search = QPushButton("Search", self.searchGroupBox)
        self.gridLayout.addWidget(self.search, 4, 0, 1, 2)

        self.verticalLayout.addWidget(self.searchGroupBox)

        self.tableWidget = QuickTableWidget(columns=9, parent=self)
        self.tableWidget.setHorizontalHeaderLabels(
            [
                "ISBN-13",
                "Title",
                "Category",
                "Author",
                "Publisher",
                "Date Published",
                "Price",
                "Total Copies",
                "Number of Copies Issued",
            ]
        )
        self.verticalLayout.addWidget(self.tableWidget)

        self.optionsHorizontalLayout = QHBoxLayout()

        self.scanISBN13 = QPushButton("Scan ISBN-13", self)
        self.optionsHorizontalLayout.addWidget(self.scanISBN13)

        self.addNewBook = QPushButton("Add New Book", self)
        self.optionsHorizontalLayout.addWidget(self.addNewBook)

        self.addCopy = QPushButton("Add Copy", self)
        self.optionsHorizontalLayout.addWidget(self.addCopy)

        self.removeCopy = QPushButton("Remove Copy", self)
        self.optionsHorizontalLayout.addWidget(self.removeCopy)

        self.verticalLayout.addLayout(self.optionsHorizontalLayout)

    def connectUi(self, parent):
        self.back.clicked.connect(parent.dashboardFunc)
        self.search.clicked.connect(self.searchFunc)
        self.scanISBN13.clicked.connect(self.scanISBN13Func)
        self.addNewBook.clicked.connect(self.addBookFunc)
        self.addCopy.clicked.connect(self.addCopyFunc)
        self.removeCopy.clicked.connect(self.removeCopyFunc)

    def searchFunc(self):
        name = self.titleLineEdit.text().strip()
        category = self.categoryComboBox.currentText()
        author = self.authorLineEdit.text().strip()
        publisher = self.publisherLineEdit.text().strip()
        self.lastSQL = f"""
SELECT B.*, COUNT(C.copy_id) total, COUNT(I.issue_id) issued
FROM books B LEFT JOIN copies C ON C.isbn_13_fk = B.isbn_13
LEFT JOIN issues I ON C.copy_id=I.copy_id_fk
WHERE B.title LIKE '%{name}%' AND B.author LIKE '%{author}%'
AND B.publisher LIKE '%{publisher}%' AND B.category LIKE '%{category}%'
GROUP BY B.isbn_13;
"""
        self.refreshTable()

    def scanISBN13Func(self):
        isbn = ScanISBN13(self).exec_()
        if not isbn:
            return
        self.lastSQL = f"""
SELECT B.*, COUNT(C.copy_id) total, COUNT(I.issue_id) issued
FROM books B LEFT JOIN copies C ON C.isbn_13_fk = B.isbn_13
LEFT JOIN issues I ON C.copy_id=I.copy_id_fk
GROUP BY B.isbn_13 HAVING B.isbn_13 = '{isbn}';
"""
        self.refreshTable()

    def addBookFunc(self):
        AddBook(self).exec_()
        self.refreshTable()

    def addCopyFunc(self):
        isbn = ScanISBN13(self).exec_()
        if not isbn:
            return
        sql = f"""
SELECT B.title, COUNT(C.isbn_13_fk)
FROM books B JOIN copies C ON C.isbn_13_fk=B.isbn_13
GROUP BY B.isbn_13 HAVING B.isbn_13='{isbn}';
"""
        self.cursor.execute(sql)
        name, copy = self.cursor.fetchone()
        date = str(QDate.currentDate().toPython())
        uuid = str(uuid4())
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Save QR code as", f"{name} {copy+1} {date}.png", "PNG Image"
        )
        if filePath:
            qrcode.make(uuid).save(filePath)
            self.cursor.execute(f"INSERT INTO copies VALUES ('{uuid}', '{isbn}', '{date}', 0);")
        self.refreshTable()

    def removeCopyFunc(self):
        sql = "SELECT copy_id FROM books WHERE copy_id='{}';"
        qr = ScanQR(self, sql, "Scan Copy ID").exec_()
        if not qr:
            return
        self.cursor.execute(f"SELECT issue_id FROM issues WHERE copy_id_fk='{qr}';")
        _ = self.cursor.fetchall()
        if self.cursor.rowcount > 0:
            QMessageBox.warning(self, "Cannot Remove Copy", "This copy is issued.")
            return
        self.cursor.execute(f"DELETE FROM copies WHERE copy_id='{qr}';")
        self.refreshTable()

    def refreshTable(self):
        self.cursor.execute(self.lastSQL)
        self.tableWidget.setData(self.cursor.fetchall())
