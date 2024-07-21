from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QComboBox
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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QMessageBox, QProgressBar, QScrollArea, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
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
import math 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QTabWidget, QPushButton, QVBoxLayout, QFileDialog
from piston_single import process_single_tdms_file 
import fitz

logger = logging.getLogger(__name__)

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


class UnitDisplayWindow(QMainWindow):
    def __init__(self, parameters, tdms_file_path, previous_window=None, tdms_file_count=0):
        super().__init__()
        self.setWindowTitle("Units of Parameters")
        self.setGeometry(100, 100, 1050, 750)
        self.parameters = parameters
        self.tdms_file_path = tdms_file_path
        self.previous_window = previous_window
        self.tdms_file_count = tdms_file_count
        logger.info("Unit display window opened")
        self.showMaximized()
        
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
        tdms_count = sum(1 for file in os.listdir(self.tdms_file_path) if file.lower().endswith('.tdms'))
        print(f"UnitDisplayWindow: Counted TDMS files: {tdms_count}")
        self.display_window = DisplayWindow(self.parameters, self.tdms_file_path, previous_window=self, tdms_file_count=tdms_count)
        self.display_window.show()
        
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
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
        
class ZoomablePlot(FigureCanvas):
    def __init__(self, fig):
        super().__init__(fig)
        self.setParent(None)
        self.figure = fig
        self.toolbar = NavigationToolbar2QT(self, self)

class DisplayWindow(QMainWindow):
    def __init__(self, parameters, tdms_file_path, previous_window, tdms_file_count, parent=None):
        super().__init__()
        self.setWindowTitle("TDMS Data")
        self.setGeometry(100, 100, 1350, 930)
        self.setMinimumSize(850, 650)
        self.parameters = parameters
        self.tdms_file_path = tdms_file_path
        self.previous_window = previous_window
        self.tdms_file_count = tdms_file_count
        self.max_overall_efficiency = self.calculate_max_overall_efficiency()
        print(f"Init: TDMS file count: {self.tdms_file_count}")
        print(f"Init: Max OE: {self.max_overall_efficiency}")
        self.showMaximized()
        

        logger.info("Displaying data")
        
        # Set background image
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\Gui_Piston\Danfoss_BG.png")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.main_layout.addWidget(self.button_previous)

        # Read max_derived_displacement before 
        self.max_derived_displacement = self.read_max_derived_displacement()

        self.create_summary_tab()
        self.create_features_tab()
        self.create_performance_tab()
        self.create_statistics_tab()
        self.create_outliers_tab()
        self.create_plot_tabs()
        self.create_pivot_tabs()
        self.create_efficiency_contour_plots()
        self.create_test_operator_tab()
        self.create_pdf_download_tab()
        self.create_help_tab()
        
        
    def get_tdms_file_count(self):
        tdms_count = sum(1 for file in os.listdir(self.tdms_file_path) if file.lower().endswith('.tdms'))
        print(f"TDMS files found: {tdms_count}")
        return tdms_count

    def calculate_max_overall_efficiency(self):
        csv_file_path = os.path.join(self.tdms_file_path, 'results', 'processed_combined_data.csv')
        print(f"Looking for CSV file at: {csv_file_path}")
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path)
            print(f"Columns in CSV file: {df.columns}")
            if 'Calc_OE' in df.columns:
                max_oe = df['Calc_OE'].max()
                print(f"Max OE found in CSV: {max_oe:.2f}%")
                return max_oe
        else:
            print(f"CSV file not found at {csv_file_path}")
        return 0.0

    def get_max_overall_efficiency(self):
        return self.max_overall_efficiency

        
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\Gui_Piston\Danfoss_BG.png")
        super().resizeEvent(event)
        
    
    def create_summary_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # Create summary table
        summary_table = QTableWidget(5, 2)
        summary_table.setHorizontalHeaderLabels(["Metric", "Value"])
        summary_table.verticalHeader().setVisible(False)
        summary_table.horizontalHeader().setStretchLastSection(True)

        # 1. Total TDMS files
        tdms_count = self.get_tdms_file_count()
        summary_table.setItem(0, 0, QTableWidgetItem("Total TDMS files"))
        summary_table.setItem(0, 1, QTableWidgetItem(str(tdms_count)))

        # 2. Highest overall efficiency
        max_oe = self.get_max_overall_efficiency()
        summary_table.setItem(1, 0, QTableWidgetItem("Highest Overall Efficiency"))
        summary_table.setItem(1, 1, QTableWidgetItem(f"{max_oe:.2f}%"))

        # 3. Number of outliers
        outlier_count = self.get_outlier_count()
        summary_table.setItem(2, 0, QTableWidgetItem("Number of Outliers"))
        summary_table.setItem(2, 1, QTableWidgetItem(str(outlier_count)))

        # 4. Test status based on outlier count
        test_status = self.get_test_status(outlier_count)
        summary_table.setItem(3, 0, QTableWidgetItem("Test Status"))
        summary_table.setItem(3, 1, QTableWidgetItem(test_status))

        # 5. Outlier count condition
        outlier_condition = self.get_outlier_condition(outlier_count)
        summary_table.setItem(4, 0, QTableWidgetItem("Outlier Count Condition"))
        summary_table.setItem(4, 1, QTableWidgetItem(outlier_condition))

        tab_layout.addWidget(summary_table)

        # Add legend for outlier count conditions
        legend_label = QLabel("Legend for Outlier Count Conditions:")
        tab_layout.addWidget(legend_label)

        legend_table = QTableWidget(3, 2)
        legend_table.setHorizontalHeaderLabels(["Condition", "Status"])
        legend_table.verticalHeader().setVisible(False)
        legend_table.horizontalHeader().setStretchLastSection(True)

        legend_table.setItem(0, 0, QTableWidgetItem("Outliers < 5"))
        legend_table.setItem(0, 1, QTableWidgetItem("Pass"))
        legend_table.setItem(1, 0, QTableWidgetItem("5 ≤ Outliers ≤ 10"))
        legend_table.setItem(1, 1, QTableWidgetItem("Under Review"))
        legend_table.setItem(2, 0, QTableWidgetItem("Outliers > 10"))
        legend_table.setItem(2, 1, QTableWidgetItem("Fail"))

        tab_layout.addWidget(legend_table)

        self.tabs.insertTab(0, tab, "Summary")
        
    

    def get_outlier_count(self):
        outliers_data = self.get_outliers_data()
        if outliers_data is not None:
            return len(outliers_data)
        return 0

    def get_test_status(self, outlier_count):
        if outlier_count < 5:
            return "Pass"
        elif 5 <= outlier_count <= 10:
            return "Under Review"
        else:
            return "Fail"

    def get_outlier_condition(self, outlier_count):
        if outlier_count < 5:
            return "Outliers < 5"
        elif 5 <= outlier_count <= 10:
            return "5 ≤ Outliers ≤ 10"
        else:
            return "Outliers > 10"
    
    def create_features_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)  # Use a different name for the layout

        table = QTableWidget(len(self.parameters), 2)
        table.setHorizontalHeaderLabels(["Parameter", "Value"])
        table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: red; }")
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)

        for row, (param, value) in enumerate(self.parameters.items()):
            table.setItem(row, 0, QTableWidgetItem(param))
            table.setItem(row, 1, QTableWidgetItem(value))

        tab_layout.addWidget(table)
        self.tabs.addTab(tab, "Features")

    def create_performance_tab(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        if os.path.exists(performance_file_path):
            df = pd.read_excel(performance_file_path, sheet_name='All Data')
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            table = QTableWidget()
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df[numeric_columns] = df[numeric_columns].round(2)
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels([str(col) for col in df.columns])
            table.setRowCount(len(df))
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

            tab_layout.addWidget(table)
            self.tabs.addTab(tab, "Performance Data")
    
    
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
            self.tabs.addTab(tab, "General Plots")
    
    def add_plot_tab(self, name, filename):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        plot_label = QLabel()
        plot_path = os.path.join(self.tdms_file_path, 'results', filename)
        
        if os.path.exists(plot_path):
            pixmap = QPixmap(plot_path)
            plot_label.setPixmap(pixmap)
            plot_label.setScaledContents(True)
        else:
            plot_label.setText(f"Plot not found: {filename}")
        
        scroll_area.setWidget(plot_label)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab, name)
    #Import QPainter 
    def create_plot_tabs(self):
        plot_files = ['flow_line_plot.png', 'efficiency_map_plot.png', 
                      ]
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
                self.tabs.addTab(tab, plot_file.split('.')[0])

        
        self.create_general_plots_tab()
        
    def read_max_derived_displacement(self):
        performance_file_path = os.path.join(self.tdms_file_path, 'results', 'performance.xlsx')
        try:
            if not os.path.exists(performance_file_path):
                logger.error(f"File not found: {performance_file_path}")
                return None

            xls = pd.ExcelFile(performance_file_path)
            logger.info(f"Available sheets: {xls.sheet_names}")

            if 'Parameters' not in xls.sheet_names:
                logger.error(f"'Parameters' sheet not found in {performance_file_path}")
                # Create the 'Parameters' sheet with default values
                logger.info("Creating 'Parameters' sheet with default values")
                df = pd.DataFrame({'max_derived_displacement': [100.0]})  # Replace with actual default value
                with pd.ExcelWriter(performance_file_path, mode='a', engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Parameters', index=False)
                logger.info(f"'Parameters' sheet created with max_derived_displacement: {df['max_derived_displacement'].iloc[0]}")
                return df['max_derived_displacement'].iloc[0]

            df = pd.read_excel(performance_file_path, sheet_name='Parameters')
            logger.info(f"Contents of 'Parameters' sheet: {df.head()}")
            max_derived_displacement = df['max_derived_displacement'].iloc[0]
            logger.info(f"Read max_derived_displacement: {max_derived_displacement}")
            return max_derived_displacement
        except FileNotFoundError:
            logger.error(f"File not found: {performance_file_path}")
        except ValueError as e:
            logger.error(f"Error reading 'Parameters' sheet: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return None
    
    def display_data(self):
        if self.max_derived_displacement is None:
            logger.error("max_derived_displacement is not available. Cannot create efficiency plots.")
            return
        logger.info("Displaying data")
    
    def create_efficiency_contour_plots(self):
        if self.max_derived_displacement is None:
            logging.error("max_derived_displacement is not available. Cannot create efficiency plots.")
            return
        
        csv_file_path = os.path.join(self.tdms_file_path, 'results', 'processed_combined_data.csv')
        
        if not os.path.exists(csv_file_path):
            logging.error(f"CSV file not found: {csv_file_path}")
            return

        df = pd.read_csv(csv_file_path)
        logging.info(f"Reading data from {csv_file_path}")
        logging.info(f"Columns in the dataframe: {df.columns.tolist()}")
        logging.info(f"Number of rows in the dataframe: {len(df)}")

        rpm_col = 'RPM'
        pressure_col = 'Outlet_Pressure_Psi'
        ve_col = 'Calc_VE'
        me_col = 'Calc_ME'
        oe_col = 'Calc_OE'

        if not all(col in df.columns for col in [rpm_col, pressure_col, ve_col, me_col, oe_col]):
            logging.error(f"Required columns not found. Available columns: {df.columns.tolist()}")
            return

        # Sample the data if there are too many points (optional)
        if len(df) > 10000:
            df = df.sample(n=10000, random_state=42)
            logging.info(f"Sampled {len(df)} points for plotting")


        # Create contour plots for VE, ME, and OE
        self.create_contour_plot(df, rpm_col, pressure_col, ve_col, 'Volumetric Efficiency (VE) Contour Plot w/ RPM and Pressure', 've_contour_plot.png')
        self.create_contour_plot(df, rpm_col, pressure_col, me_col, 'Mechanical Efficiency (ME) Contour Plot w/ RPM and Pressure', 'me_contour_plot.png')
        self.create_contour_plot(df, rpm_col, pressure_col, oe_col, 'Overall Efficiency (OE) Contour Plot w/ RPM and Pressure', 'oe_contour_plot.png')
        self.max_overall_efficiency = df[oe_col].max()

    def calculate_ve(self, df, max_derived_displacement):
        return df['Mean_Displacement'] * 100 / max_derived_displacement

    def calculate_me(self, df, max_derived_displacement, torque_col):
        return 100 * ((((max_derived_displacement / 16.387064) * df['Mean_Outlet_Pressure_Psi']) / (2 * math.pi)) /
                      df[torque_col])

    def calculate_oe(self, df, max_derived_displacement, torque_col):
        return self.calculate_ve(df, max_derived_displacement) * self.calculate_me(df, max_derived_displacement, torque_col) / 100

    def create_contour_plot(self, df, rpm_col, pressure_col, efficiency_col, title, filename):
        Y = df[rpm_col].values
        X = df[pressure_col].values
        Z = df[efficiency_col].values

        # Remove NaN values
        mask = ~np.isnan(X) & ~np.isnan(Y) & ~np.isnan(Z)
        X = X[mask]
        Y = Y[mask]
        Z = Z[mask]

        fig, ax = plt.subplots(figsize=(10, 6))
        if len(X) < 4:
            scatter = ax.scatter(X, Y, c=Z, cmap='viridis', s=10, alpha=0.5)
            plt.colorbar(scatter, label=f'{efficiency_col} (%)')
        else:
            contour = ax.tricontourf(X, Y, Z, levels=20, cmap='viridis', extend='both')
            scatter = ax.scatter(X, Y, c=Z, cmap='viridis', s=10, alpha=0.5, edgecolors='none')
            plt.colorbar(contour, label=f'{efficiency_col} (%)')

        ax.set_xlabel(f'Outlet Pressure ({pressure_col})')
        ax.set_ylabel(f'Speed ({rpm_col})')
        ax.set_title(title)
        
        
        high_efficiency_text = "High Efficiency (>75%)"
        medium_efficiency_text = "Medium Efficiency (40-75%)"
        low_efficiency_text = "Low Efficiency (<40%)"

        # Determine the coordinates for placing the text
        high_efficiency_coords = (np.mean(X[Z > 75]), np.mean(Y[Z > 75]))
        medium_efficiency_coords = (np.mean(X[(Z > 40) & (Z <= 75)]), np.mean(Y[(Z > 40) & (Z <= 75)]))
        low_efficiency_coords = (np.mean(X[Z <= 40]), np.mean(Y[Z <= 40]))

        # Add the text annotations to the plot
        if not np.isnan(high_efficiency_coords).any():
            ax.text(high_efficiency_coords[0], high_efficiency_coords[1], high_efficiency_text, fontsize=10, color='white', ha='center', va='center', bbox=dict(facecolor='green', alpha=0.5))
        if not np.isnan(medium_efficiency_coords).any():
            ax.text(medium_efficiency_coords[0], medium_efficiency_coords[1], medium_efficiency_text, fontsize=10, color='white', ha='center', va='center', bbox=dict(facecolor='yellow', alpha=0.5))
        if not np.isnan(low_efficiency_coords).any():
            ax.text(low_efficiency_coords[0], low_efficiency_coords[1], low_efficiency_text, fontsize=10, color='white', ha='center', va='center', bbox=dict(facecolor='red', alpha=0.5))

        

        plot_path = os.path.join(self.tdms_file_path, 'results', filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

        # Create a QPixmap from the saved plot
        pixmap = QPixmap(plot_path)
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)

        # Use ZoomableGraphicsView for zooming capability
        view = ZoomableGraphicsView(scene)
        view.setRenderHint(QPainter.Antialiasing)
        view.setRenderHint(QPainter.SmoothPixmapTransform)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # Create a new tab with the zoomable view
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(view)
        self.tabs.addTab(tab, title)
    
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
                    
                    self.tabs.addTab(tab, sheet_name)
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
            self.tabs.addTab(tab, "Statistics")
    
    
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
            
            self.tabs.addTab(tab, "Outliers")
    
    def create_test_operator_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        button_upload = QPushButton("Upload Single TDMS File")
        button_upload.clicked.connect(self.upload_single_tdms)
        tab_layout.addWidget(button_upload)

        self.single_file_plot_area = QScrollArea()
        self.single_file_plot_area.setWidgetResizable(True)
        tab_layout.addWidget(self.single_file_plot_area)

        self.tabs.addTab(tab, "Test Operator")

    def upload_single_tdms(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select TDMS File", "", "TDMS Files (*.tdms)")
        if file_path:
            output_path = os.path.join(os.path.dirname(file_path), 'single_file_results')
            df, max_derived_displacement, max_efficiency, plot_paths = process_single_tdms_file(file_path, output_path)
            if df is not None:
                self.display_single_file_results(plot_paths, max_efficiency, os.path.basename(file_path))

    def display_single_file_results(self, plot_paths, single_file_max_efficiency, file_name):
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Read the CSV file
        csv_path = os.path.join(os.path.dirname(list(plot_paths.values())[0]), 'single_file_processed_data.csv')
        df = pd.read_csv(csv_path)

        self.single_file_plots = []  # Store plot data for PDF

        # Display general plots
        columns_to_plot = ['Main_Flow_GPM', 'RPM', 'Outlet_Pressure_Psi', 'Pump_Torque_In.lbf', 
                           'Displacement', 'Calc_VE', 'Calc_ME', 'Calc_OE']
        for column in columns_to_plot:
            if column in df.columns:
                fig, ax = plt.subplots(figsize=(8, 6))
                canvas = FigureCanvas(fig)
                toolbar = NavigationToolbar(canvas, scroll_widget)
                
                ax.plot(df.index, df[column])
                ax.set_title(column)
                ax.set_xlabel('Time')
                ax.set_ylabel(column)
                
                min_val = df[column].min()
                max_val = df[column].max()
                avg_val = df[column].mean()
                
                ax.scatter(df[column].idxmin(), min_val, color='blue', s=100, zorder=5, label=f'Min: {min_val:.2f}')
                ax.scatter(df[column].idxmax(), max_val, color='red', s=100, zorder=5, label=f'Max: {max_val:.2f}')
                ax.scatter(df.index[len(df)//2], avg_val, color='green', s=100, zorder=5, label=f'Avg: {avg_val:.2f}')
                
                ax.legend()
                fig.tight_layout()
                
                scroll_layout.addWidget(toolbar)
                scroll_layout.addWidget(canvas)

                # Save plot data for PDF
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                self.single_file_plots.append((column, img_buffer))
            else:
                print(f"Column {column} not found in the data")

        # Display efficiency plots
        if 'efficiency' in plot_paths:
            efficiency_label = QLabel()
            efficiency_pixmap = QPixmap(plot_paths['efficiency'])
            efficiency_label.setPixmap(efficiency_pixmap.scaled(800, 300, Qt.KeepAspectRatio))
            scroll_layout.addWidget(efficiency_label)

        # Create and display efficiency comparison table
        comparison_table = QTableWidget(2, 2)
        comparison_table.setHorizontalHeaderLabels(["Overall Max Efficiency", "Single File Max Efficiency"])
        comparison_table.setItem(0, 0, QTableWidgetItem(f"{self.max_overall_efficiency:.2f}%"))
        comparison_table.setItem(0, 1, QTableWidgetItem(f"{single_file_max_efficiency:.2f}%"))
        scroll_layout.addWidget(comparison_table)

        # Add efficiency comparison text
        if single_file_max_efficiency > self.max_overall_efficiency:
            comparison_text = "The single file's efficiency is higher than the overall efficiency."
        else:
            comparison_text = "The single file's efficiency is lower than or equal to the overall efficiency."
        comparison_label = QLabel(comparison_text)
        scroll_layout.addWidget(comparison_label)
        
        self.efficiency_comparison = {
            "Overall Max Efficiency": f"{self.max_overall_efficiency:.2f}%",
            "Single File Max Efficiency": f"{single_file_max_efficiency:.2f}%",
            "Comparison": "Single file efficiency is higher" if single_file_max_efficiency > self.max_overall_efficiency else "Single file efficiency is lower or equal"
        }
        logging.debug(f"Efficiency comparison data created: {self.efficiency_comparison}")

    
        
        self.single_file_name = file_name
        logging.debug(f"Single file name stored: {self.single_file_name}")

        
        self.single_file_plots = plot_paths
        logging.debug(f"Single file plots stored: {self.single_file_plots}")

        scroll_area.setWidget(scroll_widget)
        self.single_file_plot_area.setWidget(scroll_area)
    
    
    def create_pdf_download_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        button_download = QPushButton("Download PDF Report")
        button_download.clicked.connect(self.generate_pdf_report)
        tab_layout.addWidget(button_download)

        self.tabs.addTab(tab, "Download Report")
        
    def create_help_tab(self):
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)

        pdf_path = r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\Gui_Piston\Rep_19.pdf"  # Replace with actual path
        doc = fitz.open(pdf_path)

        for page_num in range(min(2, doc.page_count)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            
            label = QLabel()
            pixmap = QPixmap.fromImage(img)
            label.setPixmap(pixmap)
            help_layout.addWidget(label)

        doc.close()

        scroll_area = QScrollArea()
        scroll_area.setWidget(help_tab)
        scroll_area.setWidgetResizable(True)

        self.tabs.addTab(scroll_area, "Help")

    def generate_pdf_report(self):
        output_path = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)")[0]
        if output_path:
            data = {}
            images = {}
            
            # Collect summary data
            summary_data = self.get_summary_data()
            data["Summary"] = summary_data

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
            
            logo_path = r"C:\Users\U436445\OneDrive - Danfoss\Documents\GitHub\Gui_Piston\Danfoss_BG.png"

            # Include single file plots if available
            if hasattr(self, 'single_file_plots'):
                create_pdf_report(data, images, output_path, logo_path, single_file_plots=self.single_file_plots, single_file_name=self.single_file_name)
            else:
                create_pdf_report(data, images, output_path, logo_path)
                
            if hasattr(self, 'single_file_plots') or hasattr(self, 'efficiency_comparison'):
                logging.debug(f"Single file plots being passed to PDF: {self.single_file_plots}")
                logging.debug(f"Type of single_file_plots: {type(self.single_file_plots)}")
                logging.debug(f"Efficiency comparison being passed to PDF: {self.efficiency_comparison}")
                create_pdf_report(data, images, output_path, logo_path, 
                                  single_file_plots=self.single_file_plots, 
                                  single_file_name=self.single_file_name,
                                  efficiency_comparison=self.efficiency_comparison)
            else:
                create_pdf_report(data, images, output_path, logo_path)

            QMessageBox.information(self, "Success", "PDF report has been generated successfully!")
            
    
    def get_summary_data(self):
        return {
            "Total TDMS files": self.get_tdms_file_count(),
            "Highest Overall Efficiency": f"{self.get_max_overall_efficiency():.2f}%",
            "Number of Outliers": self.get_outlier_count(),
            "Test Status": self.get_test_status(self.get_outlier_count()),
            "Outlier Count Condition": self.get_outlier_condition(self.get_outlier_count())
        }
    
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
                    outliers_with_tdms = outliers[['TDMS file', column]]  # Include 'TDMS file' column first
                    outliers_with_tdms['Outlier Type'] = np.where(outliers[column] > upper_bound, 'Upper', 'Lower')
                    outliers_data.append(outliers_with_tdms)

            if outliers_data:
                outliers_df = pd.concat(outliers_data, axis=0)
                # Reorder columns to put 'TDMS file' first and 'Outlier Type' last
                columns = ['TDMS file'] + [col for col in outliers_df.columns if col not in ['TDMS file', 'Outlier Type']] + ['Outlier Type']
                outliers_df = outliers_df[columns]
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