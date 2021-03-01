from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from app.utils import *


class MemberInfo(QDialog):
    def __init__(self, parent, member_id):
        super().__init__(parent)
        self.cursor = parent.cursor
        self.member_id = member_id
        self.setupUi()
        self.connectUi()

    def setupUi(self):
        self.setWindowTitle("Member Information")
        self.resize(750, 500)
        self.verticalLayout = QVBoxLayout(self)

        self.detailsGroupBox = QGroupBox(self)
        self.detailsGroupBox.setTitle("Member Details")

        self.gridLayout = QGridLayout(self.detailsGroupBox)

        self.firstNameLabel = QLabel("First Name", self.detailsGroupBox)
        self.gridLayout.addWidget(self.firstNameLabel, 0, 0, 1, 1)

        sql = f"""
SELECT first_name, last_name, email, membership_plan
FROM members WHERE member_id='{self.member_id}';
"""
        self.cursor.execute(sql)
        (
            self.fname,
            self.lname,
            self.email,
            self.membershipName,
        ) = self.cursor.fetchone()

        self.firstName = QLabel(self.fname, self.detailsGroupBox)
        self.gridLayout.addWidget(self.firstName, 0, 1, 1, 1)

        self.lastNameLabel = QLabel("Last Name", self.detailsGroupBox)
        self.gridLayout.addWidget(self.lastNameLabel, 1, 0, 1, 1)

        self.lastName = QLabel(self.lname, self.detailsGroupBox)
        self.gridLayout.addWidget(self.lastName, 1, 1, 1, 1)

        self.emailLabel = QLabel("Email", self.detailsGroupBox)
        self.gridLayout.addWidget(self.emailLabel, 2, 0, 1, 1)

        self.emailLineEdit = QLineEdit(self.detailsGroupBox)
        self.emailLineEdit.setText(self.email)
        self.gridLayout.addWidget(self.emailLineEdit, 2, 1, 1, 1)

        self.updateEmail = QPushButton("Update", self.detailsGroupBox)
        self.updateEmail.setEnabled(False)
        self.gridLayout.addWidget(self.updateEmail, 2, 2, 1, 1)

        self.membershipLabel = QLabel("Membership Type", self.detailsGroupBox)
        self.gridLayout.addWidget(self.membershipLabel, 3, 0, 1, 1)

        self.membershipComboBox = QuickComboBox(
            "SELECT title FROM membership_plans;",
            parent=self.detailsGroupBox,
        )
        i = self.membershipComboBox.findText(self.membershipName)
        self.membershipComboBox.setCurrentIndex(i)
        self.gridLayout.addWidget(self.membershipComboBox, 3, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()

        self.renewMembership = QPushButton("Renew", self.detailsGroupBox)
        self.horizontalLayout.addWidget(self.renewMembership)

        self.updateMembership = QPushButton("Update", self.detailsGroupBox)
        self.updateMembership.setEnabled(False)
        self.horizontalLayout.addWidget(self.updateMembership)

        self.gridLayout.addLayout(self.horizontalLayout, 3, 2, 1, 1)

        self.verticalLayout.addWidget(self.detailsGroupBox)

        self.booksBorrowedLabel = QLabel("Books Borrowed", self)
        self.verticalLayout.addWidget(self.booksBorrowedLabel)

        self.tableWidget = QuickTableWidget(columns=4, parent=self)
        self.tableWidget.setHorizontalHeaderLabels(["Title", "Issued On", "Due On", "Fine"])
        sql = f"""
SELECT B.title, I.issued_on, I.due_on, I.fine FROM books B
JOIN copies C ON B.isbn_13 = C.isbn_13_fk
JOIN issues I ON C.copy_id = I.copy_id_fk
WHERE I.issued_to='{self.member_id}';
"""
        self.cursor.execute(sql)
        self.tableWidget.setData(self.cursor.fetchall())
        self.verticalLayout.addWidget(self.tableWidget)

        self.downloadID = QPushButton("Download Member ID card", self)
        self.verticalLayout.addWidget(self.downloadID)

    def connectUi(self):
        self.membershipComboBox.currentTextChanged.connect(self.membershipChanged)
        self.emailLineEdit.textChanged.connect(
            lambda newStr: self.updateEmail.setEnabled(newStr != self.email)
        )
        self.updateEmail.clicked.connect(self.updateEmailFunc)
        self.renewMembership.clicked.connect(self.renewMembershipFunc)
        self.updateMembership.clicked.connect(self.updateMembershipFunc)
        self.downloadID.clicked.connect(self.downloadIDFunc)

    def membershipChanged(self, newSelection):
        self.updateMembership.setEnabled(self.membershipName != newSelection)
        self.renewMembership.setEnabled(self.membershipName == newSelection)

    def updateEmailFunc(self):
        email = self.emailLineEdit.text()
        self.cursor.execute(f"SELECT email FROM members WHERE email='{email}';")
        _ = self.cursor.fetchall()
        if self.cursor.rowcount > 0:
            QMessageBox.warning(self, "Cannot Update Email", "Email already exists.")
            return
        self.cursor.execute(
            f"UPDATE members SET email='{email}' WHERE member_id='{self.member_id}';"
        )
        self.email = email
        self.updateEmail.setEnabled(False)

    def renewMembershipFunc(self):
        exp = str(QDate.currentDate().addYears(1).toPython())
        self.cursor.execute(
            f"UPDATE members SET expiry_date='{exp}' WHERE member_id='{self.member_id}';"
        )
        self.renewMembership.setEnabled(False)

    def updateMembershipFunc(self):
        membershipName = self.membershipComboBox.currentText()
        sql = f"""
UPDATE members SET membership_plan='{membershipName}'
WHERE member_id='{self.member_id}';
"""
        self.cursor.execute(sql)
        self.membershipName = membershipName
        self.updateMembership.setEnabled(False)

    def downloadIDFunc(self):
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save ID as",
            f"{self.fname} {self.lname} {self.membershipName}.png",
            "PNG Image",
        )
        if not filePath:
            return
        sql = f"SELECT gender, doj, expiry_date FROM members WHERE member_id='{self.member_id}';"
        self.cursor.execute(sql)
        gender, doj, expiryDate = self.cursor.fetchone()
        data = {
            "First Name": self.fname,
            "Last Name": self.lname,
            "Gender": gender,
            "Date Of Joining": doj,
            "Membership Type": self.membershipName,
            "Expiry Date": expiryDate,
        }
        createQRID(self.member_id, data).save(filePath)
