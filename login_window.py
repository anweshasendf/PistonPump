import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_credentials(user_id, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = cursor.fetchone()
    conn.close()
    return result

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("App launched")
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 600, 300)
        
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label_user_id = QLabel("User ID")
        self.layout.addWidget(self.label_user_id)
        self.entry_user_id = QLineEdit()
        self.layout.addWidget(self.entry_user_id)

        self.label_password = QLabel("Password")
        self.layout.addWidget(self.label_password)
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.entry_password)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.validate_login)
        self.layout.addWidget(self.button_login)

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        super().resizeEvent(event)

    def validate_login(self):
        user_id = self.entry_user_id.text()
        password = self.entry_password.text()
        logger.info(f"Login attempt: User ID - {user_id}")
        if check_credentials(user_id, password):
            logger.info("Login successful")
            self.close()
            self.option_window = OptionWindow(previous_window=self)
            self.option_window.show()
        else:
            logger.info("Login failed")
            QMessageBox.critical(self, "Error", "Invalid credentials")

class OptionWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Select Option")
        self.setGeometry(100, 100, 600, 250)
        logger.info("Option window opened")
        
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_efficiency = QPushButton("Efficiency")
        self.button_efficiency.clicked.connect(self.open_efficiency_options)
        self.layout.addWidget(self.button_efficiency)

        self.button_hydrostatic = QPushButton("Hydrostatic")
        self.button_hydrostatic.clicked.connect(self.open_hydrostatic_options)
        self.layout.addWidget(self.button_hydrostatic)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        super().resizeEvent(event)

    def open_efficiency_options(self):
        from efficiency_window import EfficiencyWindow
        self.close()
        self.efficiency_window = EfficiencyWindow(previous_window=self)
        self.efficiency_window.show()

    def open_hydrostatic_options(self):
        from efficiency_window import HydrostaticWindow
        self.close()
        self.hydrostatic_window = HydrostaticWindow(previous_window=self)
        self.hydrostatic_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()