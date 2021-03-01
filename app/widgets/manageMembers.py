from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app import cursor
from app.dialogs import AddMember, MemberInfo, ScanQR
from app.utils import *


class ManageMembers(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.setupUi(parent)
        self.connectUi(parent)
        self.lastSQL = "SELECT 0 FROM dual WHERE false;"

    def setupUi(self, parent):
        parent.setWindowTitle("Manage Members")

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

        self.membershipTypeLabel = QLabel("Membership Type", self.searchGroupBox)
        self.gridLayout.addWidget(self.membershipTypeLabel, 4, 0, 1, 1)

        self.membershipComboBox = QuickComboBox(
            "SELECT title FROM membership_plans;",
            null=True,
            parent=self.searchGroupBox,
        )
        self.gridLayout.addWidget(self.membershipComboBox, 4, 1, 1, 3)

        self.search = QPushButton("Search", self.searchGroupBox)
        self.gridLayout.addWidget(self.search, 5, 1, 1, 3)

        self.verticalLayout.addWidget(self.searchGroupBox)

        self.tableWidget = QuickTableWidget(columns=9, parent=self)
        self.tableWidget.setHorizontalHeaderLabels(
            [
                "Member ID",
                "First Name",
                "Last Name",
                "Gender",
                "Date of birth",
                "Date of joining",
                "Email",
                "Membership Type",
                "Expiry Date",
            ]
        )
        self.tableWidget.hideColumn(0)
        self.verticalLayout.addWidget(self.tableWidget)

        self.optionsHorizontalLayout = QHBoxLayout()

        self.scanQR = QPushButton("Scan QR Code", self)
        self.optionsHorizontalLayout.addWidget(self.scanQR)

        self.addNewMember = QPushButton("Add New Member", self)
        self.optionsHorizontalLayout.addWidget(self.addNewMember)

        self.information = QPushButton("View/Edit Member Information", self)
        self.optionsHorizontalLayout.addWidget(self.information)

        self.removeMember = QPushButton("Remove Member", self)
        self.optionsHorizontalLayout.addWidget(self.removeMember)

        self.verticalLayout.addLayout(self.optionsHorizontalLayout)

    def connectUi(self, parent):
        self.back.clicked.connect(parent.dashboardFunc)
        self.search.clicked.connect(self.searchFunc)
        self.scanQR.clicked.connect(self.scanQRFunc)
        self.addNewMember.clicked.connect(self.addMemberFunc)
        self.information.clicked.connect(self.showMemberInfo)
        self.removeMember.clicked.connect(self.removeMemberFunc)

    def searchFunc(self):
        name = self.nameLineEdit.text()
        joinedAfter = str(self.joinedAfterDateEdit.date().toPython())
        joinedBefore = str(self.joinedBeforeDateEdit.date().toPython())
        membershipType = self.membershipComboBox.currentText()
        self.lastSQL = f"""
SELECT * FROM members WHERE CONCAT(first_name, ' ', last_name) LIKE '%{name}%'
AND '{joinedAfter}' < doj <= '{joinedBefore}' AND membership_plan LIKE '%{membershipType}%';
"""
        self.refreshTable()

    def scanQRFunc(self):
        sql = "SELECT member_id FROM members WHERE member_id='{}'"
        memberQR = ScanQR(self, sql, prompt="Scan QR code of member").exec_()
        if not memberQR:
            return
        self.lastSQL = f"SELECT * FROM members WHERE member_id = '{memberQR}';"
        self.refreshTable()

    def addMemberFunc(self):
        AddMember(self).exec_()
        self.refreshTable()

    def showMemberInfo(self):
        r = self.tableWidget.currentRow()
        if r < 0:
            return
        member_id = self.tableWidget.item(r, 0).text()
        MemberInfo(self, member_id).exec_()
        self.refreshTable()

    def removeMemberFunc(self):
        sql = "SELECT member_id FROM members WHERE member_id='{}'"
        memberQR = ScanQR(self, sql, prompt="Scan QR code of member").exec_()
        if not memberQR:
            return
        self.cursor.execute(f"SELECT COUNT(*) FROM issues WHERE issued_to='{memberQR}';")
        issues = self.cursor.fetchone()[0]
        if issues:
            QMessageBox.warning(
                self, "Cannot Delete Member", "Cannot delete member with active issues."
            )
            return
        self.cursor.execute(f"DELETE FROM members WHERE member_id='{memberQR}';")
        self.refreshTable()

    def refreshTable(self):
        self.cursor.execute(self.lastSQL)
        self.tableWidget.setData(self.cursor.fetchall())