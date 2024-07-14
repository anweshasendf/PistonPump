import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow

if __name__ == "__main__":
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