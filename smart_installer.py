# ===============================================================
# 🧠 StackCheckMate Smart Installer (Windows Edition)
# Product of Quick Red Tech
# Owned by Chisom Life Eke
# ===============================================================

import sys
import os
import requests
import tempfile
import subprocess
import shutil
import ctypes
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox, QMenuBar, QMenu
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QThread, Signal


# ===============================================================
# 🔐 ADMIN PRIVILEGE CHECK
# ===============================================================
def ensure_admin_privileges():
    """
    Ensures the script runs with administrator rights.
    If not, prompts the user and restarts the script with elevated privileges.
    """
    try:
        # Check if running as admin
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        reply = QMessageBox.question(
            None,
            "Administrator Permission Required",
            "⚠️ To install StackCheckMate in Program Files, administrator rights are required.\n\n"
            "Would you like to restart the installer with admin privileges?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            # Relaunch the script with admin privileges
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, params, None, 1
                )
            except Exception as e:
                QMessageBox.critical(None, "Elevation Failed", f"❌ Could not gain admin rights:\n{e}")
            sys.exit(0)
        else:
            QMessageBox.warning(None, "Installation Cancelled",
                                "Installation requires Administrator permission.\nExiting setup.")
            sys.exit(0)


# ===============================================================
# DOWNLOAD THREAD
# ===============================================================
class DownloadThread(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)
    cancelled = False

    def __init__(self, url, dest_path):
        super().__init__()
        self.url = url
        self.dest_path = dest_path

    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=25)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(self.dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.cancelled:
                        self.error.emit("Download cancelled by user.")
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.progress.emit(percent)

            self.finished.emit(self.dest_path)

        except Exception as e:
            self.error.emit(str(e))

    def cancel_download(self):
        self.cancelled = True


# ===============================================================
# MAIN INSTALLER WINDOW
# ===============================================================
class SmartInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StackCheckMate Installer for Windows")
        self.setGeometry(480, 250, 520, 350)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #2a2a2a
                );
                color: #e6e6e6;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 17px;
                color: #00a2ff;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078d7;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #2893ff;
            }
            QProgressBar {
                border: 2px solid #0078d7;
                border-radius: 6px;
                text-align: center;
                color: white;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
            }
        """)
        self.init_ui()

    # -----------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout()

        menubar = QMenuBar(self)
        file_menu = QMenu("File", self)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(about_action)
        file_menu.addAction(exit_action)
        menubar.addMenu(file_menu)
        layout.setMenuBar(menubar)

        self.label = QLabel("🧠 StackCheckMate Smart Installer")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.os_label = QLabel("Detected: Windows 10/11 (x64)")
        self.os_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.os_label)

        self.download_btn = QPushButton("Download & Install for Windows")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("Cancel Download")
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setEnabled(False)
        layout.addWidget(self.cancel_btn)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.open_folder_btn = QPushButton("Open Installation Folder")
        self.open_folder_btn.clicked.connect(self.open_install_folder)
        self.open_folder_btn.setEnabled(False)
        layout.addWidget(self.open_folder_btn)

        self.setLayout(layout)

    # -----------------------------------------------------------
    def show_about(self):
        QMessageBox.information(
            self, "About StackCheckMate",
            (
                "🧠 StackCheckMate Smart Installer (Windows Edition)\n"
                "Product of Quick Red Tech\n"
                "Owned by Chisom Life Eke\n\n"
                "Automatically downloads and installs the latest StackCheckMate build for Windows."
            )
        )

    # -----------------------------------------------------------
    # -----------------------------------------------------------
    def start_download(self):
        tmp_dir = tempfile.gettempdir()
        # ✅ Updated download URL to your GitHub direct file link
        file_url = "https://github.com/elchisomeke-dev/stackcheckmate/raw/main/STACKCHECKMATE%20SOFTWARE/dist/StackCheckMate.exe"
        self.temp_path = os.path.join(tmp_dir, "StackCheckMate.exe")

        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.label.setText("📦 Downloading StackCheckMate for Windows...")

        self.download_thread = DownloadThread(file_url, self.temp_path)
        self.download_thread.progress.connect(self.progress.setValue)
        self.download_thread.finished.connect(self.install_app)
        self.download_thread.error.connect(self.download_failed)
        self.download_thread.start()

    # -----------------------------------------------------------
    def cancel_download(self):
        if hasattr(self, 'download_thread'):
            self.download_thread.cancel_download()
            self.download_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.label.setText("❌ Download cancelled by user.")

    # -----------------------------------------------------------
    def download_failed(self, err):
        QMessageBox.critical(self, "Download Failed", f"❌ Error: {err}")
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.label.setText("❌ Download failed. Try again.")

    # -----------------------------------------------------------
    def install_app(self, file_path):
        self.cancel_btn.setEnabled(False)
        self.label.setText("⚙️ Installing StackCheckMate...")

        try:
            target_dir = r"C:\Program Files\StackCheckMate"
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, "StackCheckMate.exe")
            shutil.move(file_path, target_path)

            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            shortcut_path = os.path.join(desktop, "StackCheckMate.lnk")

            powershell_script = f'''
            $WshShell = New-Object -ComObject WScript.Shell;
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}");
            $Shortcut.TargetPath = "{target_path}";
            $Shortcut.Save();
            '''
            subprocess.run(["powershell", "-Command", powershell_script], check=False)

            QMessageBox.information(
                self, "Installation Complete",
                f"✅ StackCheckMate installed successfully to:\n{target_dir}\n\n"
                "A shortcut was added to your Desktop."
            )
            self.open_folder_btn.setEnabled(True)
            self.install_path = target_dir
            self.label.setText("✅ Installation Complete!")

        except PermissionError:
            QMessageBox.critical(
                self, "Permission Error",
                "You must run this installer as Administrator to install in Program Files."
            )
            self.label.setText("❌ Installation failed - Admin required.")
        except Exception as e:
            QMessageBox.critical(self, "Installation Error", f"❌ {e}")
            self.label.setText("❌ Installation failed.")
        finally:
            self.download_btn.setEnabled(True)

    # -----------------------------------------------------------
    def open_install_folder(self):
        if hasattr(self, 'install_path') and os.path.exists(self.install_path):
            subprocess.Popen(f'explorer "{self.install_path}"')
        else:
            QMessageBox.warning(self, "Not Found", "Installation folder not found.")


# ===============================================================
# MAIN EXECUTION
# ===============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ensure_admin_privileges()  # ✅ Ask for admin before proceeding
    window = SmartInstaller()
    window.show()
    sys.exit(app.exec())