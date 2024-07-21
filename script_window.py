from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import logging
import sys
import os
import pandas as pd
from io import BytesIO
from PIL import Image
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QMessageBox, QProgressBar, QScrollArea
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
from PyQt5.QtGui import QPainter
#import ZoomableGraphicsView
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout, QLabel
import logging
import io
import time
import shutil
from scipy import stats
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QMessageBox, QProgressBar, QScrollArea, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
import logging
from io import BytesIO
from PIL import Image
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QMessageBox, QProgressBar, QScrollArea
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QPixmap, QImage
import logging
import json 
import sqlite3
from nptdms import TdmsFile
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
from display_window import *

logger = logging.getLogger(__name__)

class ScriptUploadWindow(QMainWindow):
    def __init__(self, folder_path, script_path, previous_window=None, data=None, tdms_file_count=0):
        super().__init__()
        self.folder_path = folder_path
        self.previous_window = previous_window
        self.data = data
        self.script_path = script_path
        self.tdms_file_count = tdms_file_count
        self.parameters = {}  # Initialize an empty dictionary for parameters
        self.setWindowTitle("Script Upload Indicator")
        self.setGeometry(100, 100, 1050, 750)
        logger.info("Script upload window opened")
        self.showMaximized()
        
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        #self.button_upload_script = QPushButton("Run Script")
        #self.button_upload_script.clicked.connect(self.upload_script)
        #self.layout.addWidget(self.button_upload_script)
        
        self.button_run_script = QPushButton("Run Script")
        self.button_run_script.clicked.connect(self.run_script)
        self.layout.addWidget(self.button_run_script)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

       
        self.process = QProcess(self)
        self.process.finished.connect(self.on_process_finished)
        self.process.readyReadStandardOutput.connect(self.on_ready_read_standard_output)
        self.process.readyReadStandardError.connect(self.on_ready_read_standard_error)
        self.process.errorOccurred.connect(self.on_error_occurred)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)
        
        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.on_process_timeout)
        
         # Automatically trigger script upload
        QTimer.singleShot(0, self.run_script)
        

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        super().resizeEvent(event)

    #def upload_script(self):
      #  file_path, _ = QFileDialog.getOpenFileName(self, "Select Script File", "", "Python Files (*.py)")
      #  if file_path:
          #  logger.info(f"Script uploaded: {file_path}")
         #   with open(file_path, 'r') as file:
          #      script_content = file.read()
           # self.close()
           # self.parameter_edit_window = ParameterEditWindow(tdms_file_path=self.folder_path, previous_window=self, script_content=script_content, data=self.data)
          #  self.parameter_edit_window.show()
    def upload_script(self):
        logger.info(f"Script uploaded: {self.script_path}")
        # Process the script here
        self.process_script()
        
    def process_script(self):
        # ... (script processing code )

        self.close()
        self.display_window = DisplayWindow(self.parameters, self.folder_path, previous_window=self)
        self.display_window.show()
    
    def run_script(self):
        logger.info("Starting script execution")
        output_path = os.path.join(self.folder_path, 'results')
        os.makedirs(output_path, exist_ok=True)
        command = [sys.executable, self.script_path, self.folder_path, output_path]
        logger.info(f"Executing command: {' '.join(command)}")
        self.process.start(sys.executable, command[1:])
        self.timeout_timer.start(300000)  # 5 minutes timeout
        self.progress_bar.setVisible(True)
        self.button_run_script.setEnabled(False)

    def on_process_finished(self, exit_code, exit_status):
        self.timeout_timer.stop()
        logger.info(f"Script execution finished with exit code {exit_code} and exit status {exit_status}")
        self.progress_bar.setVisible(False)  # Hide the progress bar
        self.button_run_script.setEnabled(True)
        stdout = self.process.readAllStandardOutput().data().decode()
        stderr = self.process.readAllStandardError().data().decode()
        
        logger.debug(f"Script stdout: {stdout}")
        logger.debug(f"Script stderr: {stderr}")
        
        if exit_code == 0:
            self.load_parameters()
            self.open_parameter_edit_window()
        else:
            error_message = f"Script execution failed with exit code {exit_code}."
            if stderr:
                try:
                    error_data = json.loads(stderr)
                    error_message += f"\nError: {error_data.get('error', 'Unknown error')}"
                except json.JSONDecodeError:
                    error_message += f"\nStderr: {stderr}"
            logger.error(error_message)
            self.on_error_occurred(error_message)

    def on_ready_read_standard_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        logger.debug(f"Script output: {output}")

    def on_ready_read_standard_error(self):
        error_output = self.process.readAllStandardError().data().decode()
        logger.error(f"Script in output: {error_output}")

    def on_error_occurred(self, error_message):
        logger.error(f"Script error: {error_message}")
        self.progress_bar.setVisible(False)  # Hide the progress bar
        self.button_upload_script.setEnabled(True)  # Re-enable the button
        QMessageBox.critical(self, "Error", f"Script execution failed: {error_message}")

    def on_process_timeout(self):
        logger.error("Script execution timed out")
        self.process.kill()
        self.on_error_occurred("Script execution timed out after 5 minutes")
        
    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()
    def load_parameters(self):
        # Load parameters from the results of the script execution
        
        parameters_file = os.path.join(self.folder_path, 'results', 'parameters.json')
        if os.path.exists(parameters_file):
            with open(parameters_file, 'r') as f:
                self.parameters = json.load(f)
        else:
            logger.warning("Parameters file not found. Using default parameters.")
            self.parameters = {
                "Displacement": "18cc",
                "Speed - rpm": "Up to 3600",
                "Pressure rating - bar (psi)": "Nominal - 210 (4060)",
                "Control": "Pressure only compensator",
                "Shaft Options - SAE": "9T (210 bar)",
                "Main Ports": "Rear Port\tDelivery Port 1.0625-12 SAE O-ring;\nSuction Port 1.625-12 SAE O-ring"
            }
    def open_parameter_edit_window(self):
        self.parameter_edit_window = ParameterEditWindow(self.folder_path, previous_window=self, data=self.parameters, tdms_file_count=self.tdms_file_count)
        self.parameter_edit_window.show()
        self.close()

class ParameterEditWindow(QMainWindow):
    def __init__(self, tdms_file_path, previous_window=None, script_content=None, data=None, tdms_file_count=0):
        super().__init__()
        self.previous_window = previous_window
        self.script_content = script_content
        self.data = data
        self.tdms_file_count = tdms_file_count
        self.showMaximized()
        
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        self.setWindowTitle("Edit Parameters")
        self.setGeometry(100, 100, 1050, 750)
        self.tdms_file_path = tdms_file_path
        logger.info("Parameter edit window opened")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.parameters = {
            "Displacement": "18cc",
            "Speed - rpm": "Up to 3600",
            "Pressure rating - bar (psi)": "Nominal - 210 (4060)",
            "Control": "Pressure only compensator",
            "Shaft Options - SAE": "9T (210 bar)",
            "Main Ports": "Rear Port\tDelivery Port 1.0625-12 SAE O-ring;\nSuction",
            "Main Ports": "Rear Port\tDelivery Port 1.0625-12 SAE O-ring;\nSuction Port 1.625-12 SAE O-ring"
        }

        self.table = QTableWidget(len(self.parameters), 2)
        self.table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: red; }")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        for row, (param, value) in enumerate(self.parameters.items()):
            self.table.setItem(row, 0, QTableWidgetItem(param))
            self.table.setItem(row, 1, QTableWidgetItem(value))

        self.layout.addWidget(self.table)

        self.button_confirm = QPushButton("Confirm")
        self.button_confirm.clicked.connect(self.confirm_parameters)
        
        self.layout.addWidget(self.button_confirm)
        
        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)
        
    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()
            
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        super().resizeEvent(event)

    def confirm_parameters(self):
        for row in range(self.table.rowCount()):
            param = self.table.item(row, 0).text()
            value = self.table.item(row, 1).text()
            self.parameters[param] = value
            
        self.close()
        self.unit_display_window = UnitDisplayWindow(self.parameters, self.tdms_file_path, previous_window=self, tdms_file_count=self.tdms_file_count)

        self.unit_display_window.show()


    
    