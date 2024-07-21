import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow

#Works with login_window -> efficiency_window -> tdms_widnow -> script_window -> display_window -> gui_pdf

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    
    stylesheet = """
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 20px;
        font-weight: bold;
    }
    QPushButton {
        font-size: 20px;
        font-weight: bold;
        padding: 8px 16px;
        background-color: #D22B2B;
        color: white;
        border: none;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #C04000;
    }
    QPushButton:pressed {
        background-color: #004275;
    }
    QLabel {
        font-size: 18px;
    }
    QLineEdit {
        font-size: 18px;
        padding: 6px;
        border: 1px solid #BDBDBD;
        border-radius: 4px;
    }
    QTableWidget {
        font-size: 16px;
        gridline-color: #E0E0E0;
    }
    QTableWidget::item {
        padding: 6px;
    }
    QHeaderView::section {
        background-color: #F5F5F5;
        font-weight: bold;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #E0E0E0;
    }
    QMessageBox {
        font-size: 18px;
    }
    QTabWidget::pane {
        border: 1px solid #E0E0E0;
    }
    QTabBar::tab {
        background-color: #F5F5F5;
        padding: 10px 20px;
        border: 1px solid #E0E0E0;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 1px solid white;
    }
    """
    app.setStyleSheet(stylesheet)
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())