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
from guipdf import create_pdf_report


# Configure logging to output to the console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
def check_credentials(user_id, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = cursor.fetchone()
    conn.close()
    return result

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("App launched")
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 600, 300)
        
        # Set background image
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
        
        # Set background image
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
        self.close()
        self.efficiency_window = EfficiencyWindow(previous_window=self)
        self.efficiency_window.show()

    def open_hydrostatic_options(self):
        self.close()
        self.hydrostatic_window = HydrostaticWindow(previous_window=self)
        self.hydrostatic_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()

class EfficiencyWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Efficiency Options")
        self.setGeometry(100, 100, 600, 300)
        logger.info("Efficiency options window opened")
        
        # Set background image
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
        self.close()
        self.tdms_type_window = TDMSTypeWindow(previous_window=self)
        self.tdms_type_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()


class TDMSTypeWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Choose TDMS Type")
        self.setGeometry(100, 100, 400, 200)
        logger.info("TDMS Type selection window opened")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_single = QPushButton("Single TDMS Folder")
        self.button_single.clicked.connect(self.open_single_upload)
        self.layout.addWidget(self.button_single)

        self.button_coupled = QPushButton("Coupled TDMS Folder")
        self.button_coupled.clicked.connect(self.open_coupled_upload)
        self.layout.addWidget(self.button_coupled)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)

    def open_single_upload(self):
        logger.info("Single TDMS folder selected")
        self.close()
        self.upload_window = UploadWindow(previous_window=self)
        self.upload_window.show()

    def open_coupled_upload(self):
        logger.info("Coupled TDMS folder selected")
        self.close()
        self.coupled_upload_window = CoupledUploadWindow(previous_window=self)
        self.coupled_upload_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()



class UploadWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Upload Folder")
        self.setGeometry(100, 100, 600, 250)
        logger.info("Upload window opened")
        
        # Set background image
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_upload_folder = QPushButton("Upload TDMS Folder")
        self.button_upload_folder.clicked.connect(self.read_tdms_folder)
        self.layout.addWidget(self.button_upload_folder)

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

    def read_tdms_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select TDMS Folder")
        if folder_path:
            logger.info(f"Folder uploaded: {folder_path}")
            data = {}
            seen_files = set()
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    if file_name.endswith('.tdms'):
                        if file_name in seen_files:
                            logger.warning(f"Duplicate file ignored: {file_name}")
                            continue
                        seen_files.add(file_name)
                        file_path = os.path.join(root, file_name)
                        tdms_file = TdmsFile.read(file_path)
                        for group in tdms_file.groups():
                            if group.name == 'piston_group':
                                df = group.as_dataframe()
                                if group.name not in data:
                                    data[group.name] = df
                                else:
                                    try:
                                        data[group.name] = pd.concat([data[group.name], df]).drop_duplicates().reset_index(drop=True)
                                    except Exception as e:
                                        logger.error(f"Error concatenating data for file {file_name}: {e}")
            self.close()
            self.script_upload_window = ScriptUploadWindow(folder_path, previous_window=self)
            self.script_upload_window.show()

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()

class CoupledUploadWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Upload Coupled TDMS Folder")
        self.setGeometry(100, 100, 600, 250)
        logger.info("Coupled Upload window opened")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_upload_folder = QPushButton("Upload Coupled TDMS Folder")
        self.button_upload_folder.clicked.connect(self.upload_coupled_folder)
        self.layout.addWidget(self.button_upload_folder)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)

    def upload_coupled_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Coupled TDMS Folder")
        if folder_path:
            logger.info(f"Coupled folder uploaded: {folder_path}")
            self.combine_tdms_files(folder_path)
            self.close()
            self.script_upload_window = ScriptUploadWindow(folder_path, previous_window=self)
            self.script_upload_window.show()

    def combine_tdms_files(self, folder_path):
        logger.info(f"Combining TDMS files in {folder_path}")
        tdms_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.tdms'):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(folder_path, file)
                    if source_path != dest_path:
                        shutil.copy2(source_path, dest_path)
                        logger.info(f"Copied {source_path} to {dest_path}")
                    tdms_files.append(dest_path)
        logger.info(f"Combined {len(tdms_files)} TDMS files in {folder_path}")

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()


class ScriptUploadWindow(QMainWindow):
    #def __init__(self, data, tdms_file_path, is_folder=False, previous_window=None):
    def __init__(self, tdms_folder_path, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Upload Python Script")
        self.setGeometry(100, 100, 600, 250)
        self.tdms_folder_path = tdms_folder_path
        logger.info("Script upload window opened")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_upload_script = QPushButton("Upload Python Script")
        self.button_upload_script.clicked.connect(self.upload_script)
        self.layout.addWidget(self.button_upload_script)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress bar
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)

        self.process = QProcess(self)
        self.process.finished.connect(self.on_process_finished)
        self.process.readyReadStandardOutput.connect(self.on_ready_read_standard_output)
        self.process.readyReadStandardError.connect(self.on_ready_read_standard_error)

        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.on_process_timeout)


    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        super().resizeEvent(event)

    def upload_script(self):
        script_path, _ = QFileDialog.getOpenFileName(self, "Open Python Script", "", "Python files (*.py)")
        if script_path:
            logger.info(f"Script uploaded: {script_path}")
            self.button_upload_script.setEnabled(False)  # Disable the button to prevent second input
            self.progress_bar.setVisible(True)  # Show the progress bar
            self.run_script(script_path)

    def run_script(self, script_path):
        #logger.info("Starting script execution")
        #data_json = json.dumps(self.data)
        #output_path = os.path.join(self.tdms_file_path, 'results')
        #os.makedirs(output_path, exist_ok=True)
        #command = [sys.executable, script_path, data_json, output_path]
        #logger.info(f"Executing command: {' '.join(command)}")
        #self.process.start(sys.executable, command[1:])
        #self.timeout_timer.start(300000)  # 5 minutes timeout
        
        logger.info("Starting script execution")
        output_path = os.path.join(self.tdms_folder_path, 'results')
        os.makedirs(output_path, exist_ok=True)
        command = [sys.executable, script_path, self.tdms_folder_path, output_path]
        logger.info(f"Executing command: {' '.join(command)}")
        self.process.start(sys.executable, command[1:])
        self.timeout_timer.start(300000)

    def on_process_finished(self, exit_code, exit_status):
        self.timeout_timer.stop()
        logger.info(f"Script execution finished with exit code {exit_code} and exit status {exit_status}")
        self.progress_bar.setVisible(False)  # Hide the progress bar
        
        stdout = self.process.readAllStandardOutput().data().decode()
        stderr = self.process.readAllStandardError().data().decode()
        
        logger.debug(f"Script stdout: {stdout}")
        logger.debug(f"Script stderr: {stderr}")
        
        if exit_code == 0:
            self.parameter_edit_window = ParameterEditWindow(self.tdms_folder_path, previous_window=self)
            self.parameter_edit_window.show()
            self.close()  # Close the ScriptUploadWindow
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

class ParameterEditWindow(QMainWindow):
    def __init__(self, tdms_file_path, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Edit Parameters")
        self.setGeometry(100, 100, 600, 400)
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

    def confirm_parameters(self):
        for row in range(self.table.rowCount()):
            param = self.table.item(row, 0).text()
            value = self.table.item(row, 1).text()
            self.parameters[param] = value
            
        self.close()
        self.unit_display_window = UnitDisplayWindow(self.parameters, self.tdms_file_path, previous_window=self)
        self.unit_display_window.show()

class UnitDisplayWindow(QMainWindow):
    def __init__(self, parameters, tdms_file_path, previous_window=None):
        super().__init__()
        self.setWindowTitle("Units of Parameters")
        self.setGeometry(100, 100, 600, 400)
        self.parameters = parameters
        self.tdms_file_path = tdms_file_path
        self.previous_window = previous_window
        logger.info("Unit display window opened")
        
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")

    
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.units = {
            "TDMS file": "TDMS",
            "Speed": "RPM",
            "RPM": "RPM",
            "Outlet Pressure": "Psi",
            "Inlet_Temp_F": "F",
            "Inlet_PSI": "Psi",
            "Outlet_Pressure_Psi": "Psi",
            "Load-sense_pressure_Psi": "Psi",
            "Delta P": "Psi",
            "Pump_Torque_In.lbf": "In.lbf",
            "Pump_Case_Pressure_PSI": "Psi",
            "Main_Flow_GPM": "GPM",
            "Pump_Case Flow_gpm": "GPM",
            "Pump_Case_Temp_F": "F",
            "Control_Pressure_PSI": "Psi",
            "Swash Angle_Deg": "Deg",
            "Displacement": "cc",
            "Calc_VE" : "%",
            "Calc_ME" : "%",
            "Calc_OE" : "%",
            # Add more units as needed
        }

        self.table = QTableWidget(len(self.units), 2)
        self.table.setHorizontalHeaderLabels(["Parameter", "Unit"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        for row, (param, unit) in enumerate(self.units.items()):
            self.table.setItem(row, 0, QTableWidgetItem(param))
            self.table.setItem(row, 1, QTableWidgetItem(unit))

        self.layout.addWidget(self.table)

        self.button_confirm = QPushButton("Confirm")
        self.button_confirm.clicked.connect(self.confirm_units)
        self.layout.addWidget(self.button_confirm)

    def confirm_units(self):
        self.close()
        self.display_window = DisplayWindow(self.parameters, self.tdms_file_path, previous_window=self)
        self.display_window.show()
        
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        super().resizeEvent(event)
    
    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()

class DisplayWindow(QMainWindow):
    def __init__(self, parameters, tdms_file_path, previous_window):
        super().__init__()
        self.setWindowTitle("TDMS Data")
        self.setGeometry(100, 100, 1100, 900)
        self.setMinimumSize(850, 650)
        self.parameters = parameters
        self.tdms_file_path = tdms_file_path
        self.previous_window = previous_window
        logger.info("Displaying data")
        
        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        #self.layout.addWidget(self.button_previous)

    
        # Set background image
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        self.create_features_tab()
        self.create_performance_tab()
        self.create_plot_tabs()
        self.create_pivot_tabs()
        self.create_statistics_tab()
        self.create_outliers_tab()
        self.create_pdf_download_tab()

        
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")
        super().resizeEvent(event)
        
        
    def create_features_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        table = QTableWidget(len(self.parameters), 2)
        table.setHorizontalHeaderLabels(["Parameter", "Value"])
        table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: red; }")
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)

        for row, (param, value) in enumerate(self.parameters.items()):
            table.setItem(row, 0, QTableWidgetItem(param))
            table.setItem(row, 1, QTableWidgetItem(value))

        tab_layout.addWidget(table)
        self.tab_widget.addTab(tab, "Features")

    def create_performance_tab(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            table = QTableWidget()
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels([str(col) for col in df.columns])
            table.setRowCount(len(df))
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

            tab_layout.addWidget(table)
            self.tab_widget.addTab(tab, "Performance Data")
    
    
    def create_general_plots_tab(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)

            colors = plt.get_cmap('tab10')

            for i, column in enumerate(numeric_columns):
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(df.index, df[column], color=colors(i % 10))  # cycle through colors
                ax.set_title(column)
                ax.set_xlabel('Occurence Index')
                ax.set_ylabel(column)

                canvas = FigureCanvasQTAgg(fig)
                scroll_layout.addWidget(canvas)

            scroll_content.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_content)
            tab_layout.addWidget(scroll_area)
            self.tab_widget.addTab(tab, "General Plots")
    
         
    #Import QPainter 
    def create_plot_tabs(self):
        plot_files = ['flow_line_plot.png', 'efficiency_map_plot.png', 'oe_contour_plot.png', 
                      'me_contour_plot.png', 've_contour_plot.png']
        for plot_file in plot_files:
            plot_path = os.path.join(self.tdms_file_path, 'results', plot_file)
            if os.path.exists(plot_path):
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)

                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_content = QWidget()
                scroll_layout = QVBoxLayout(scroll_content)

                try:
                    pixmap = QPixmap(plot_path)
                    scene = QGraphicsScene()
                    item = QGraphicsPixmapItem(pixmap)
                    scene.addItem(item)

                    view = ZoomableGraphicsView(scene)
                    view.setRenderHint(QPainter.Antialiasing)
                    view.setRenderHint(QPainter.SmoothPixmapTransform)
                    view.setDragMode(QGraphicsView.ScrollHandDrag)
                    view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                    view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

                    scroll_layout.addWidget(view)
                    
                except Exception as e:
                    logger.error(f"Error creating plot: {e}")
                    label = QLabel(f"Error: {str(e)}")
                    scroll_layout.addWidget(label)

                scroll_area.setWidget(scroll_content)
                tab_layout.addWidget(scroll_area)
                self.tab_widget.addTab(tab, plot_file.split('.')[0])

        
        self.create_general_plots_tab()
        
    def create_pivot_tabs(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            pivot_sheets = ['VE Pivot', 'ME Pivot', 'OE Pivot']
            for sheet_name in pivot_sheets:
                try:
                    df = pd.read_excel(performance_file_path, sheet_name=sheet_name)
                    tab = QWidget()
                    tab_layout = QVBoxLayout(tab)

                    table = QTableWidget()
                    table.setColumnCount(len(df.columns))
                    table.setHorizontalHeaderLabels([str(col) for col in df.columns])
                    table.setRowCount(len(df))
                    for i in range(len(df)):
                        for j in range(len(df.columns)):
                            table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
                    tab_layout.addWidget(table)
                    
                    self.tab_widget.addTab(tab, sheet_name)
                except ValueError as e:
                    logger.error(f"Error reading sheet {sheet_name}: {e}")
    
    def create_statistics_tab(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            table = QTableWidget(len(numeric_columns), 6)
            table.setHorizontalHeaderLabels(["Column", "Min", "Max", "Average", "Median", "IQR"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)

            for row, column in enumerate(numeric_columns):
                table.setItem(row, 0, QTableWidgetItem(column))
                table.setItem(row, 1, QTableWidgetItem(f"{df[column].min():.2f}"))
                table.setItem(row, 2, QTableWidgetItem(f"{df[column].max():.2f}"))
                table.setItem(row, 3, QTableWidgetItem(f"{df[column].mean():.2f}"))
                table.setItem(row, 4, QTableWidgetItem(f"{df[column].median():.2f}"))
                q1, q3 = df[column].quantile([0.25, 0.75])
                iqr = q3 - q1
                table.setItem(row, 5, QTableWidgetItem(f"{iqr:.2f}"))

            tab_layout.addWidget(table)
            self.tab_widget.addTab(tab, "Statistics")
    
    
    def create_outliers_tab(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            
            tab = QWidget()
            tab_layout = QHBoxLayout(tab)
            
            table = QTableWidget(len(df), len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            for col, column in enumerate(df.columns):
                if pd.api.types.is_numeric_dtype(df[column]):
                    q1 = df[column].quantile(0.25)
                    q3 = df[column].quantile(0.75)
                    iqr = q3 - q1
                    upper_fence = q3 + (1.5 * iqr)
                    lower_fence = q1 - (1.5 * iqr)
                    col_max = df[column].max()
                    col_min = df[column].min()
                    
                    for row, value in enumerate(df[column]):
                        item = QTableWidgetItem(f"{value:.2f}")
                        if value > upper_fence:
                            item.setBackground(QBrush(QColor("red")))
                        elif value < lower_fence:
                            item.setBackground(QBrush(QColor("blue")))
                        if value == col_max:
                            item.setBackground(QBrush(QColor("orange")))
                        elif value == col_min:
                            item.setBackground(QBrush(QColor("pink")))
                        table.setItem(row, col, item)
                else:
                    for row, value in enumerate(df[column]):
                        table.setItem(row, col, QTableWidgetItem(str(value)))
            
            tab_layout.addWidget(table)
            
            # Create legend
            legend_layout = QVBoxLayout()
            legend_items = [
                ("Red", "Upper outlier"),
                ("Blue", "Lower outlier"),
                ("Orange", "Maximum value"),
                ("Pink", "Minimum value")
            ]
            for color, description in legend_items:
                legend_item = QHBoxLayout()
                color_box = QLabel()
                color_box.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
                color_box.setFixedSize(20, 20)
                legend_item.addWidget(color_box)
                legend_item.addWidget(QLabel(description))
                legend_layout.addLayout(legend_item)
            
            legend_layout.addStretch()
            tab_layout.addLayout(legend_layout)
            
            self.tab_widget.addTab(tab, "Outliers")
    
    def create_pdf_download_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        button_download = QPushButton("Download PDF Report")
        button_download.clicked.connect(self.generate_pdf_report)
        tab_layout.addWidget(button_download)

        self.tab_widget.addTab(tab, "Download Report")

    def generate_pdf_report(self):
        output_path = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)")[0]
        if output_path:
            data = {}
            images = {}

            # Collect data from performance tab
            performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
            if os.path.exists(performance_file_path):
                data["Performance Data"] = pd.read_excel(performance_file_path, sheet_name='All Data')

            # Collect data from statistics tab
            statistics_data = self.get_statistics_data()
            if statistics_data is not None:
                data["Statistics"] = statistics_data

            # Collect data from outliers tab
            outliers_data = self.get_outliers_data()
            if outliers_data is not None:
                data["Outliers"] = outliers_data

            pivot_sheets = ['VE Pivot', 'ME Pivot', 'OE Pivot']
            for sheet_name in pivot_sheets:
                pivot_data = self.get_pivot_data(sheet_name)
                if pivot_data is not None:
                    data[sheet_name] = pivot_data



            # Collect images from plot tabs
            plot_files = ['flow_line_plot.png', 'efficiency_map_plot.png', 'oe_contour_plot.png', 
                          'me_contour_plot.png', 've_contour_plot.png']
            for plot_file in plot_files:
                plot_path = os.path.join(self.tdms_file_path, 'results', plot_file)
                if os.path.exists(plot_path):
                    images[plot_file.split('.')[0]] = plot_path

            
            general_plots = self.get_general_plots()
            images.update(general_plots)
            
            logo_path = r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png"
            create_pdf_report(data, images, output_path, logo_path)
            QMessageBox.information(self, "Success", "PDF report has been generated successfully!")
    
    def get_performance_data(self):
        # Implement this method to return the performance data as a DataFrame
        pass

    def get_statistics_data(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            stats_data = []
            for column in numeric_columns:
                stats = df[column].agg(['min', 'max', 'mean', 'median'])
                q1, q3 = df[column].quantile([0.25, 0.75])
                iqr = q3 - q1
                stats['IQR'] = iqr
                stats_data.append(stats)

            stats_df = pd.DataFrame(stats_data, index=numeric_columns)
            stats_df = stats_df.reset_index()
            stats_df.columns = ['Column', 'Min', 'Max', 'Average', 'Median', 'IQR']
            return stats_df
        return None

    

    def get_outliers_data(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            outliers_data = []
            for column in numeric_columns:
                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                if not outliers.empty:
                    outliers_data.append(outliers[[column]])

            if outliers_data:
                outliers_df = pd.concat(outliers_data, axis=1)
                return outliers_df
        return None

    
    def get_pivot_data(self, sheet_name):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            try:
                df = pd.read_excel(performance_file_path, sheet_name=sheet_name)
                return df
            except ValueError:
                print(f"Sheet {sheet_name} not found in the Excel file.")
        return None


    def get_general_plots(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            plots = {}
            for column in numeric_columns:
                plt.figure(figsize=(10, 5))
                plt.plot(df.index, df[column])
                plt.title(column)
                plt.xlabel('Occurence Index')
                plt.ylabel(column)
                
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                
                plot_path = os.path.join(self.tdms_file_path, 'results', f'{column}_plot.png')
                with open(plot_path, 'wb') as f:
                    f.write(img_buffer.getvalue())
                
                plots[f'{column} Plot'] = plot_path
                plt.close()

            return plots
        return {}

                
    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()


# Main function to start the application
def main():
    app = QApplication(sys.argv)
    
    stylesheet = """
    QWidget {
        font-size: 16px;
    }
    QPushButton {
        font-size: 17px;
    }
    QLabel {
        font-size: 16px;
    }
    QLineEdit {
        font-size: 16px;
    }
    QTableWidget {
        font-size: 16px;
    }
    QMessageBox {
        font-size: 16px;
    }
    """
    app.setStyleSheet(stylesheet)
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
    
    

if __name__ == "__main__":
    main()