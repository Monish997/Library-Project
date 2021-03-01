from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app.dialogs import ScanQR
from app.utils import *
from app import cursor


class ManageIssues(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cursor = cursor
        self.setupUi(parent)
        self.connectUi(parent)
        self.lastSQL = "SELECT 0 FROM dual WHERE false;"

    def setupUi(self, parent):
        parent.setWindowTitle("Manage Issues")

        self.verticalLayout = QVBoxLayout(self)

        self.backHorizontalLayout = QHBoxLayout()

        self.back = QPushButton("Back", self)
        self.backHorizontalLayout.addWidget(self.back)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.backHorizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.backHorizontalLayout)

        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle("Search")
        self.gridLayout = QGridLayout(self.groupBox)

        self.bookTitleLabel = QLabel("Book Title", self.groupBox)
        self.gridLayout.addWidget(self.bookTitleLabel, 0, 0, 1, 1)

        self.bookTitleLineEdit = QLineEdit(self.groupBox)
        self.gridLayout.addWidget(self.bookTitleLineEdit, 0, 1, 1, 3)

        self.issuedAfterLabel = QLabel("Issued After", self.groupBox)
        self.gridLayout.addWidget(self.issuedAfterLabel, 1, 0, 1, 1)

        self.issuedAfterDateEdit = QuickDateEdit(self.groupBox)
        self.gridLayout.addWidget(self.issuedAfterDateEdit, 1, 1, 1, 1)

        self.issuedBeforeLabel = QLabel("Before", self.groupBox)
        self.gridLayout.addWidget(self.issuedBeforeLabel, 1, 2, 1, 1)

        self.issuedBeforeDateEdit = QuickDateEdit(self.groupBox)
        self.issuedBeforeDateEdit.setDate(QDate.currentDate())
        self.gridLayout.addWidget(self.issuedBeforeDateEdit, 1, 3, 1, 1)

        self.minFineLabel = QLabel("Fine Amount From", self.groupBox)
        self.gridLayout.addWidget(self.minFineLabel, 2, 0, 1, 1)

        self.minFineLineEdit = QLineEdit(self.groupBox)
        self.minFineLineEdit.setValidator(QIntValidator())
        self.gridLayout.addWidget(self.minFineLineEdit, 2, 1, 1, 1)

        self.maxFineLabel = QLabel("To", self.groupBox)
        self.gridLayout.addWidget(self.maxFineLabel, 2, 2, 1, 1)

        self.maxFineLineEdit = QLineEdit(self.groupBox)
        self.maxFineLineEdit.setValidator(QIntValidator())
        self.gridLayout.addWidget(self.maxFineLineEdit, 2, 3, 1, 1)

        self.search = QPushButton("Search", self.groupBox)
        self.gridLayout.addWidget(self.search, 6, 1, 1, 3)

        self.verticalLayout.addWidget(self.groupBox)

        self.tableWidget = QuickTableWidget(columns=6, parent=self)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Copy ID", "Title", "Member Name", "Issued on", "Due on", "Fine"]
        )
        self.tableWidget.hideColumn(0)
        self.verticalLayout.addWidget(self.tableWidget)

        self.backHorizontalLayout = QHBoxLayout()

        self.issueCopy = QPushButton("Issue Copy", self)
        self.backHorizontalLayout.addWidget(self.issueCopy)

        self.recallCopy = QPushButton("Recall Copy", self)
        self.backHorizontalLayout.addWidget(self.recallCopy)

        self.compensateCopy = QPushButton("Compensate Copy", self)
        self.backHorizontalLayout.addWidget(self.compensateCopy)

        self.verticalLayout.addLayout(self.backHorizontalLayout)

    def connectUi(self, parent):
        self.back.clicked.connect(parent.dashboardFunc)
        self.search.clicked.connect(self.searchFunc)
        self.issueCopy.clicked.connect(self.issueCopyFunc)
        self.recallCopy.clicked.connect(self.recallCopyFunc)
        self.compensateCopy.clicked.connect(self.compensateCopyFunc)

    def searchFunc(self):
        title = self.bookTitleLineEdit.text().strip()
        maxFine = int(self.maxFineLineEdit.text() or 0)
        minFine = int(self.minFineLineEdit.text() or 0)
        issuedAfter = str(self.issuedAfterDateEdit.date().toPython())
        issuedBefore = str(self.issuedBeforeDateEdit.date().toPython())
        self.lastSQL = f"""
SELECT I.copy_id_fk, B.title, CONCAT(M.first_name, ' ', M.last_name), I.issued_on, I.due_on, I.fine
FROM books B JOIN copies C ON B.isbn_13 = C.isbn_13_fk
JOIN issues I ON C.copy_id = I.copy_id_fk
JOIN members M ON I.issued_to = M.member_id
WHERE B.title LIKE '%{title}%'
AND '{issuedAfter}' < I.issued_on <= '{issuedBefore}'
AND I.fine >= {minFine}"""
        if maxFine:
            self.lastSQL += f" AND I.fine <= {maxFine}"
        self.lastSQL += ";"
        self.refreshTable()

    def issueCopyFunc(self):
        sql = "SELECT copy_id FROM copies WHERE copy_id = '{}';"
        copyQR = ScanQR(self, sql, prompt="Scan QR code of Copy").exec_()
        if not copyQR:
            return
        self.cursor.execute(f"SELECT copy_id_fk from issues WHERE copy_id_fk='{copyQR}';")
        _ = self.cursor.fetchall()
        if self.cursor.rowcount > 0:
            QMessageBox.warning(self, "Cannot Issue Copy", "Copy already issued.")
            return
        sql = "SELECT member_id FROM members WHERE member_id='{}';"
        memberQR = ScanQR(self, sql, prompt="Scan QR code of Member").exec_()
        if not memberQR:
            return
        sql = f"""
SELECT MP.borrow_limit, IFNULL(COUNT(I.issue_id), 0) FROM members M JOIN membership_plans MP
ON MP.title = M.membership_plan LEFT JOIN issues I ON I.issued_to = M.member_id
WHERE M.member_id = '{memberQR}'
GROUP BY M.member_id;
"""
        self.cursor.execute(sql)
        limit, count = self.cursor.fetchone()
        if count == limit:
            QMessageBox.warning(
                self,
                "Cannot Issue Copy",
                "The Member has already reached the borrow limit.",
            )
            return
        date = str(QDate.currentDate().toPython())
        due = str(QDate.currentDate().addDays(7).toPython())
        sql = f"""
INSERT INTO issues (copy_id_fk, issued_on, issued_to, due_on)
VALUES ('{copyQR}', '{date}', '{memberQR}', '{due}');
"""
        self.cursor.execute(sql)
        self.refreshTable()

    def recallCopyFunc(self):
        sql = "SELECT copy_id FROM copies WHERE copy_id = '{}';"
        copyQR = ScanQR(self, sql, prompt="Scan QR code of copy").exec_()
        if not copyQR:
            return
        self.cursor.execute(f"SELECT issue_id from issues where copy_id_fk = '{copyQR}';")
        _ = self.cursor.fetchall()
        if self.cursor.rowcount == 0:
            QMessageBox(self, "Cannot Recall Copy", "Copy not issued")
            return
        self.cursor.execute(f"DELETE FROM issues WHERE copy_id_fk = '{copyQR}';")
        self.refreshTable()

    def compensateCopyFunc(self):
        r = self.tableWidget.currentRow()
        if r == -1:
            return
        copyQR = self.tableWidget.item(r, 0).text()
        self.cursor.execute(f"DELETE FROM issues WHERE copy_id_fk = '{copyQR}';")
        self.cursor.execute(f"DELETE FROM copies WHERE copy_id='{copyQR}';")
        self.refreshTable()

    def refreshTable(self):
        self.cursor.execute(self.lastSQL)
        self.tableWidget.setData(self.cursor.fetchall())
