from app import cursor
from app.utils import QuickTableWidget
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class ListWidget(QWidget):
    def __init__(self, parent, table, column, label) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.table, self.column, self.label = table, column, label
        self.setupUi()
        self.connectUi()

    def setupUi(self):
        self.gridLayout = QGridLayout(self)

        self.lineEdit = QLineEdit(self)
        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)

        self.insert = QPushButton("Insert", self)
        self.gridLayout.addWidget(self.insert, 0, 1, 1, 1)

        self.tableWidget = QuickTableWidget(columns=1, parent=self)
        self.tableWidget.setHorizontalHeaderLabels([f"{self.label} Name"])
        self.cursor.execute(f"SELECT {self.column} FROM {self.table};")
        self.tableWidget.setData(self.cursor.fetchall())
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 2)

    def connectUi(self):
        self.insert.clicked.connect(self.insertFunc)

    def insertFunc(self):
        text = self.lineEdit.text().strip()
        if text == "":
            QMessageBox.warning(self, "Insufficient Data", f"{self.label} name cannot be empty")
            return
        self.cursor.execute(
            f"SELECT {self.column} FROM {self.table} WHERE LOWER({self.column})='{text.lower()}';"
        )
        self.cursor.fetchall()
        if self.cursor.rowcount:
            QMessageBox.warning(self, f"{self.label} already exists", "Try another name")
            return
        self.cursor.execute(f"INSERT INTO {self.table} VALUES ('{text}');")
        self.cursor.execute(f"SELECT {self.column} FROM {self.table};")
        self.tableWidget.setData(self.cursor.fetchall())


class APC(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("More...")
        self.resize(450, 600)
        self.verticalLayout = QVBoxLayout(self)

        self.tabWidget = QTabWidget()

        self.authorTab = ListWidget(self.tabWidget, "authors", "author_name", "Author")
        self.tabWidget.addTab(self.authorTab, "Authors")

        self.publisherTab = ListWidget(self.tabWidget, "publishers", "publisher_name", "Publisher")
        self.tabWidget.addTab(self.publisherTab, "Publishers")

        self.categoryTab = ListWidget(self.tabWidget, "categories", "category_name", "Category")
        self.tabWidget.addTab(self.categoryTab, "Catgeories")

        self.verticalLayout.addWidget(self.tabWidget)
