from uuid import uuid4

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app.utils import *


class AddMember(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.cursor = parent.cursor
        self.setupUi()
        self.connectUi()

    def setupUi(self):
        self.setWindowTitle("Add Member")
        self.resize(720, 360)
        self.setModal(True)

        self.gridLayout = QGridLayout(self)

        self.firstNameLabel = QLabel("First Name", self)
        self.gridLayout.addWidget(self.firstNameLabel, 0, 0, 1, 1)

        self.firstNameLineEdit = QLineEdit(self)
        self.gridLayout.addWidget(self.firstNameLineEdit, 0, 1, 1, 1)

        self.lastNameLabel = QLabel("Last Name", self)
        self.gridLayout.addWidget(self.lastNameLabel, 1, 0, 1, 1)

        self.lastNameLineEdit = QLineEdit(self)
        self.gridLayout.addWidget(self.lastNameLineEdit, 1, 1, 1, 1)

        self.genderLabel = QLabel("Gender", self)
        self.gridLayout.addWidget(self.genderLabel, 2, 0, 1, 1)

        self.genderComboBox = QComboBox(self)
        self.genderComboBox.addItem("Male")
        self.genderComboBox.addItem("Female")
        self.gridLayout.addWidget(self.genderComboBox, 2, 1, 1, 1)

        self.dobLabel = QLabel("Date Of Birth", self)
        self.gridLayout.addWidget(self.dobLabel, 3, 0, 1, 1)

        self.dobDateEdit = QuickDateEdit(self)
        self.gridLayout.addWidget(self.dobDateEdit, 3, 1, 1, 1)

        self.emailLabel = QLabel("Email", self)
        self.gridLayout.addWidget(self.emailLabel, 4, 0, 1, 1)

        self.emailLineEdit = QLineEdit(self)
        self.gridLayout.addWidget(self.emailLineEdit, 4, 1, 1, 1)

        self.membershipPlanLabel = QLabel("Membership Plan", self)
        self.gridLayout.addWidget(self.membershipPlanLabel, 5, 0, 1, 1)

        self.membershipPlanComboBox = QuickComboBox(
            "SELECT title FROM membership_plans;", parent=self
        )
        self.gridLayout.addWidget(self.membershipPlanComboBox, 5, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)

    def connectUi(self):
        self.buttonBox.accepted.connect(self.addMemberFunc)
        self.buttonBox.rejected.connect(self.reject)

    def addMemberFunc(self):
        uuid = str(uuid4())
        fname = self.firstNameLineEdit.text().strip()
        lname = self.lastNameLineEdit.text().strip()
        gender = self.genderComboBox.currentText()
        dob = str(self.dobDateEdit.date().toPython())
        doj = str(QDate.currentDate().toPython())
        email = self.emailLineEdit.text().strip()
        membershipName = self.membershipPlanComboBox.currentText()
        expiryDate = (
            str(QDate.currentDate().addYears(1).toPython()) if membershipName != "Basic" else None
        )

        if fname and lname and email:
            fileName = f"{fname} {lname} {membershipName}"
            filePath, _ = QFileDialog.getSaveFileName(
                self, "Save ID as", f"{fileName}.png", "PNG Image"
            )
        else:
            QMessageBox.warning(
                self, "Insufficient Data", "Please fill all fields to register member."
            )
            return

        if filePath:
            data = {
                "First Name": fname,
                "Last Name": lname,
                "Gender": gender,
                "Date Of Joining": doj,
                "Membership Type": membershipName,
                "Expiry Date": expiryDate,
            }
            createQRID(uuid, data).save(filePath)
            record = f"'{uuid}', '{fname}', '{lname}', '{gender}', '{dob}', '{doj}', '{email}', '{membershipName}', "
            record += f"'{expiryDate}'" if expiryDate else "NULL"
            if expiryDate:
                self.cursor.execute(f"INSERT INTO members VALUES ({record});")
            self.accept()
        else:
            QMessageBox.warning(
                self, "Member not added", "Please save member ID to register member."
            )
            return
