import qrcode
from PIL import Image, ImageDraw, ImageFont
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app import cursor


def createQRID(guid, data):
    qr = qrcode.make(guid)
    qr = qr.resize((250, 250))

    output = Image.new("RGB", (800, 450), (255, 255, 255))
    output.paste(qr, (500, 150))

    georgiaPath = "./app/utils/Georgia.ttf"

    Font = ImageFont.truetype(georgiaPath, 50)
    Brush = ImageDraw.Draw(output)

    Brush.text((50, 50), "Equinox Library", font=Font, fill=(0, 0, 0))

    Font = ImageFont.truetype(georgiaPath, 25)

    offset = 300 // len(data)
    i = 0
    for key in data:
        Brush.text((50, 150 + i * offset), f"{key}: {data[key]}", font=Font, fill=(0, 0, 0))
        i += 1

    return output


class QuickTableWidget(QTableWidget):
    def __init__(self, columns, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setShowGrid(False)
        self.setSortingEnabled(True)
        self.setStyleSheet("background-color: white; selection-background-color: #a8cce9;")
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnCount(columns)

    def setData(self, data):
        self.setRowCount(0)
        if not data:
            return

        for j in range(len(data)):
            self.insertRow(j)
            for i in range(len(data[j])):
                item = QTableWidgetItem(str(data[j][i]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.setItem(j, i, item)


class QuickDateEdit(QDateEdit):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setCalendarPopup(True)
        self.setMaximumDate(QDate.currentDate())


class QuickComboBox(QComboBox):
    def __init__(self, sql, null=False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if null:
            self.addItem("")
        cursor.execute(sql)
        for i in cursor:
            self.addItem(i[0])
        self.setMaxVisibleItems(10)


if __name__ == "__main__":
    from PIL import ImageShow

    data = {
        "First Name": "Monish",
        "Last Name": "Sudhagar",
        "Gender": "Male",
        "Date of Joining": "2020/11/01",
        "Role": "Librarian",
    }
    ID = createQRID("c3f9d130-8524-4699-9b40-4e0f7d5bd4f5", data)
    ImageShow.show(ID)
