from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
import logging
import os
from nptdms import TdmsFile
import pandas as pd
import shutil 
from script_window import *

logger = logging.getLogger(__name__)

class TDMSTypeWindow(QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setWindowTitle("Choose TDMS Type")
        self.setGeometry(100, 100, 400, 200)
        logger.info("TDMS Type selection window opened")
        
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\GUI\Danfoss_BG.png")


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
        
        