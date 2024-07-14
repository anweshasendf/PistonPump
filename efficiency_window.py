from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class EfficiencyWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Efficiency Options")
        self.setGeometry(100, 100, 600, 300)
        logger.info("Efficiency options window opened")
        
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        options = ["Efficiency", "LS Hystersis", "LS Linearity", "LS RR", "LS Speed Sweep", "PC Hyst", "PC Speed Sweep", "PC RR"]
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(self.open_upload_window)
            self.layout.addWidget(button)

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
    
    def open_upload_window(self):
        from tdms_window import TDMSTypeWindow
        self.close()
        self.tdms_type_window = TDMSTypeWindow(previous_window=self)
        self.tdms_type_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()

class HydrostaticWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Hydrostatic Options")
        self.setGeometry(100, 100, 600, 250)
        logger.info("Hydrostatic options window opened")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        options = ["Null", "Full", "X"]
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(self.open_upload_window)
            self.layout.addWidget(button)

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
    
    def open_upload_window(self):
        from tdms_window import TDMSTypeWindow
        self.close()
        self.tdms_type_window = TDMSTypeWindow(previous_window=self)
        self.tdms_type_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()