from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app import cursor
from app.dialogs import AddStaff, ScanQR
from app.utils import *


class ManageStaff(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.setupUi(parent)
        self.connectUi(parent)
        self.lastSQL = "SELECT 0 from dual WHERE false"

    def setupUi(self, parent):
        parent.setWindowTitle("Manage Staff")

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

        self.nameLabel = QLabel("Name", self.searchGroupBox)
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)

        self.nameLineEdit = QLineEdit(self.searchGroupBox)
        self.gridLayout.addWidget(self.nameLineEdit, 0, 1, 1, 3)

        self.joinedAfterLabel = QLabel("Joined After", self.searchGroupBox)
        self.gridLayout.addWidget(self.joinedAfterLabel, 1, 0, 1, 1)

        self.joinedAfterDateEdit = QuickDateEdit(self.searchGroupBox)
        self.gridLayout.addWidget(self.joinedAfterDateEdit, 1, 1, 1, 1)

        self.joinedBeforeLabel = QLabel("Before", self.searchGroupBox)
        self.gridLayout.addWidget(self.joinedBeforeLabel, 1, 2, 1, 1)

        self.joinedBeforeDateEdit = QuickDateEdit(self.searchGroupBox)
        self.joinedBeforeDateEdit.setDate(QDate.currentDate())
        self.gridLayout.addWidget(self.joinedBeforeDateEdit, 1, 3, 1, 1)

        self.jobTitleLabel = QLabel("Job Title", self.searchGroupBox)
        self.gridLayout.addWidget(self.jobTitleLabel, 2, 0, 1, 1)

        self.jobTitleComboBox = QuickComboBox(
            "SELECT title FROM staff_levels;",
            null=True,
            parent=self.searchGroupBox,
        )
        self.gridLayout.addWidget(self.jobTitleComboBox, 2, 1, 1, 3)

        self.search = QPushButton("Search", self.searchGroupBox)
        self.gridLayout.addWidget(self.search, 3, 1, 1, 3)

        self.verticalLayout.addWidget(self.searchGroupBox)

        self.tableWidget = QuickTableWidget(columns=8, parent=self)
        self.tableWidget.setHorizontalHeaderLabels(
            [
                "Staff ID",
                "First Name",
                "Last Name",
                "Gender",
                "Date of birth",
                "Date of joining",
                "Email",
                "Job Title",
            ]
        )
        self.tableWidget.hideColumn(0)
        self.verticalLayout.addWidget(self.tableWidget)

        self.optionsHorizontalLayout = QHBoxLayout()

        self.scanQR = QPushButton("Scan QR Code", self)
        self.optionsHorizontalLayout.addWidget(self.scanQR)

        self.addNewStaff = QPushButton("Add New Staff", self)
        self.optionsHorizontalLayout.addWidget(self.addNewStaff)

        self.removeStaff = QPushButton("Remove Staff", self)
        self.optionsHorizontalLayout.addWidget(self.removeStaff)

        self.verticalLayout.addLayout(self.optionsHorizontalLayout)

    def connectUi(self, parent):
        self.back.clicked.connect(parent.dashboardFunc)
        self.search.clicked.connect(self.searchFunc)
        self.scanQR.clicked.connect(self.scanQRFunc)
        self.addNewStaff.clicked.connect(AddStaff(self, self.cursor).exec_)
        self.removeStaff.clicked.connect(self.removeStaffFunc)

    def searchFunc(self):
        name = self.nameLineEdit.text().strip()
        joinedAfter = self.joinedAfterDateEdit.date().toPython()
        joinedBefore = self.joinedBeforeDateEdit.date().toPython()
        jobTitle = self.jobTitleComboBox.currentText()
        self.lastSQL = f"""
SELECT * FROM staff WHERE CONCAT(first_name, ' ', last_name) LIKE '%{name}%'
AND '{joinedAfter}' < doj <= '{joinedBefore}' AND job_title LIKE '%{jobTitle}%';
"""
        self.refreshTable()

    def scanQRFunc(self):
        sql = "SELECT staff_id FROM staff WHERE staff_id='{}';"
        staffQR = ScanQR(self, sql, prompt="Scan QR code of staff").exec_()
        if not staffQR:
            return
        self.lastSQL = f"SELECT * FROM staff WHERE staff_id='{staffQR}';"
        self.refreshTable()

    def removeStaffFunc(self):
        sql = "SELECT staff_id FROM staff WHERE staff_id='{}';"
        staffQR = ScanQR(self, sql, prompt="Scan QR code of staff").exec_()
        if not staffQR:
            return
        self.cursor.execute(f"DELETE FROM staff WHERE staff_id='{staffQR}';")
        self.refreshTable()

    def refreshTable(self):
        self.cursor.execute(self.lastSQL)
        self.tableWidget.setData(self.cursor.fetchall())
