# import sys
# from cx_Freeze import setup, Executable

# # Increase recursion limit
# # sys.setrecursionlimit(5000)

# setup(
#     name="GUIapp",
#     version="1.0",
#     description="Python GUI Based APP for Data Visualization and Data Analysis",
#     executables=[Executable("gui_pyqt.py")],
#     options={
#         "build_exe": {
#             "include_files": ["gui_pyqt.py", "insert_user.py", "logger.py", "preprocess_script.py", "setup_db.py", "tdmsreader.py","users.db"],
#             "excludes": ["torchaudio"]  # Example of excluding a module, add more if needed
#         }
#     }
# )

import sys
from cx_Freeze import setup, Executable

# Increase recursion limit
sys.setrecursionlimit(5000)

setup(
    name="GUI_Piston_app",
    version="1.0",
    description="Python GUI Based APP for Data Visualization and Data Analysis",
    executables=[Executable("main.py")],
    options={
        "build_exe": {
            "include_files": [
                "gui_pyqt2.py",
                "insert_user.py", 
                "logger.py", 
                "setup_db.py", 
                "tdmsreader.py",
                "main.py",
                "display_window.py",
                "efficiency_window.py",
                "guipdf.py",
                "login_window.py",
                "piston_group.py",
                "script_window.py",
                "tdms_window.py",
                "users.db"  # Ensure users.db is included
            ],
            "excludes": ["tkinter"],  # Exclude unnecessary modules
            "optimize": 2  # Optimize bytecode
        }
    }
)