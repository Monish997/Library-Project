from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app.dialogs import APC
from app.widgets import ManageBooks, ManageIssues, ManageMembers, ManageStaff
from app import cursor


class Dashboard(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.setupUi(parent)
        self.connectUi(parent)

    def changePermissions(self, staff_id):
        sql = f"""
SELECT L.manage_member, L.manage_staff, L.manage_books, L.manage_issues
FROM staff_levels L JOIN staff S
ON L.title = S.job_title
WHERE S.staff_id = '{staff_id}';
"""
        self.cursor.execute(sql)
        member, staff, books, issues = self.cursor.fetchone()
        self.manageMembers.setEnabled(member)
        self.manageStaff.setEnabled(staff)
        self.manageBooks.setEnabled(books)
        self.manageIssues.setEnabled(issues)

    def setupUi(self, parent):
        parent.setWindowTitle("Dashboard")

        self.gridLayout = QGridLayout(self)

        self.headerLabel = QLabel("XYZ Library", self)
        font = QFont("Georgia", 36)
        self.headerLabel.setFont(font)
        self.headerLabel.setAlignment(Qt.AlignCenter)
        self.gridLayout.addWidget(self.headerLabel, 1, 1, 1, 1)

        self.buttonGrid = QGridLayout()

        self.manageBooks = QPushButton("Manage Books", self)
        self.manageBooks.setMinimumSize(QSize(200, 70))
        self.buttonGrid.addWidget(self.manageBooks, 0, 0, 1, 2)

        self.manageMembers = QPushButton("Manage Members", self)
        self.manageMembers.setMinimumSize(QSize(200, 70))
        self.buttonGrid.addWidget(self.manageMembers, 0, 2, 1, 2)

        self.manageIssues = QPushButton("Manage Issues", self)
        self.manageIssues.setMinimumSize(QSize(200, 70))
        self.buttonGrid.addWidget(self.manageIssues, 0, 4, 1, 2)

        self.manageStaff = QPushButton("Manage Staff", self)
        self.manageStaff.setMinimumSize(QSize(200, 70))
        self.buttonGrid.addWidget(self.manageStaff, 1, 1, 1, 2)

        self.apc = QPushButton("More...", self)
        self.apc.setMinimumSize(QSize(200, 70))
        self.buttonGrid.addWidget(self.apc, 1, 3, 1, 2)

        self.gridLayout.addLayout(self.buttonGrid, 3, 1, 1, 1)

        self.verticalSpacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(self.verticalSpacer1, 0, 1, 1, 1)

        self.verticalSpacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(self.verticalSpacer2, 2, 1, 1, 1)

        self.verticalSpacer3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(self.verticalSpacer3, 4, 1, 1, 1)

        self.horizontalSpacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer1, 3, 0, 1, 1)

        self.horizontalSpacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(self.horizontalSpacer2, 3, 2, 1, 1)

        self.logout = QPushButton("Logout", self)
        self.logout.setMinimumSize(QSize(0, 40))
        self.gridLayout.addWidget(self.logout, 5, 0, 1, 3)

    def connectUi(self, parent):
        self.manageIssues.clicked.connect(lambda: parent.switchFunc(ManageIssues))
        self.manageMembers.clicked.connect(lambda: parent.switchFunc(ManageMembers))
        self.manageBooks.clicked.connect(lambda: parent.switchFunc(ManageBooks))
        self.manageStaff.clicked.connect(lambda: parent.switchFunc(ManageStaff))
        self.apc.clicked.connect(APC(self).exec_)
        self.logout.clicked.connect(parent.logoutFunc)