from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QMenu, QMenuBar, QFileDialog, QDialogButtonBox, QDialog, QGridLayout, QGroupBox, QComboBox, QTableView, QLabel, QLineEdit
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot, Qt, QAbstractTableModel
import sys
from cryptography.fernet import Fernet
import ast

file = open("key.key", "rb")
key = file.read()
file.close()
f = Fernet(key)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Fantasy Premier League"
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        dialog = CreateAccount()
        dialog.exec()

class CreateAccount(QDialog):
    def __init__(self):
        super().__init__()

        self.width = 400
        self.height = 240

        self.namelabel = QLabel(self)
        self.namelabel.setText("Name:")
        self.nameline = QLineEdit(self)

        self.nameline.move(80, 20)
        self.nameline.resize(200, 32)
        self.namelabel.move(20, 20)

        self.passwordlabel = QLabel(self)
        self.passwordlabel.setText("Password:")
        self.passwordline = QLineEdit(self)

        self.passwordline.move(80, 80)
        self.passwordline.resize(200, 32)
        self.passwordlabel.move(20, 80)

        self.idlabel = QLabel(self)
        self.idlabel.setText("ID:")
        self.idline = QLineEdit(self)

        self.idline.move(80, 140)
        self.idline.resize(200, 32)
        self.idlabel.move(20, 140)

        self.button = QPushButton("Create account", self)
        self.button.move(20,200)
        
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        user = {"name": self.nameline.text(), "password": self.passwordline.text(), "manager_id": self.idline.text()}
        user = f.encrypt(str(user).encode("utf-8"))
        filename = "config\\"+self.nameline.text()+".cnfg"
        file = open(filename, "wb")
        file.write(user)
        file.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App() 
    sys.exit(app.exec_())