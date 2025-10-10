# ===============================================================
# StackCheckMate Smart Installer
# Product of Quick Red Tech
# Owned by Chisom Life Eke
# ===============================================================

import sys
import os
import platform
import requests
import tempfile
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox, QMenuBar, QMenu
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QThread, Signal


# -------------------------------
# DOWNLOAD THREAD
# -------------------------------
class DownloadThread(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

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
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.progress.emit(percent)

            self.finished.emit(self.dest_path)

        except Exception as e:
            self.error.emit(str(e))


# -------------------------------
# MAIN INSTALLER WINDOW
# -------------------------------
class SmartInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StackCheckMate Smart Installer")
        self.setGeometry(480, 250, 520, 320)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                color: white;
                font-family: 'Consolas';
            }
            QLabel {
                font-size: 17px;
                color: #ff4040;
            }
            QPushButton {
                background-color: #ff4040;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #ff7070;
            }
            QProgressBar {
                border: 2px solid #ff4040;
                border-radius: 6px;
                text-align: center;
                color: white;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: #ff4040;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Menu bar
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

        # Labels and controls
        self.label = QLabel("🧠 StackCheckMate Smart Installer")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.os_label = QLabel(f"Detected OS: {platform.system()} ({platform.machine()})")
        self.os_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.os_label)

        self.download_btn = QPushButton("Download & Install")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    # -------------------------------
    # INFO BOX
    # -------------------------------
    def show_about(self):
        QMessageBox.information(
            self, "About StackCheckMate",
            (
                "🧠 StackCheckMate Smart Installer\n"
                "Product of Quick Red Tech\n"
                "Owned by Chisom Life Eke\n\n"
                "Automatically detects your OS and installs the correct build."
            )
        )

    # -------------------------------
    # DOWNLOAD & INSTALL HANDLER
    # -------------------------------
    def start_download(self):
        os_name = platform.system().lower()
        tmp_dir = tempfile.gettempdir()

        # ✅ Corrected URLs for each OS (future releases ready)
        urls = {
            "windows": "https://github.com/elchisomeke-dev/stackcheckmate/releases/download/Windows/StackCheckMate.exe",
            "darwin": "https://github.com/elchisomeke-dev/stackcheckmate/releases/download/Windows/StackCheckMate-mac-os",
            "linux": "https://github.com/elchisomeke-dev/stackcheckmate/releases/download/Windows/StackCheckMate-lunix"
        }

        # Pick correct one
        if "win" in os_name:
            file_url = urls["windows"]
            dest = os.path.join(tmp_dir, "StackCheckMate.exe")
        elif "darwin" in os_name:
            file_url = urls["darwin"]
            dest = os.path.join(tmp_dir, "StackCheckMate-mac.zip")
        elif "linux" in os_name:
            file_url = urls["linux"]
            dest = os.path.join(tmp_dir, "StackCheckMate-linux.bin")
        else:
            QMessageBox.warning(self, "Error", f"Unsupported OS: {os_name}")
            return

        self.download_btn.setEnabled(False)
        self.label.setText("📦 Downloading StackCheckMate...")

        self.download_thread = DownloadThread(file_url, dest)
        self.download_thread.progress.connect(self.progress.setValue)
        self.download_thread.finished.connect(self.install_app)
        self.download_thread.error.connect(lambda e: self.download_failed(e))
        self.download_thread.start()

    # -------------------------------
    # DOWNLOAD ERROR HANDLER
    # -------------------------------
    def download_failed(self, err):
        QMessageBox.critical(self, "Download Failed", f"❌ Error: {err}")
        self.download_btn.setEnabled(True)
        self.label.setText("❌ Download failed. Try again.")

    # -------------------------------
    # INSTALLATION
    # -------------------------------
    def install_app(self, file_path):
        self.label.setText("⚙️ Installing StackCheckMate...")
        try:
            if file_path.endswith(".exe"):
                os.startfile(file_path)
            elif file_path.endswith(".zip"):
                subprocess.run(["unzip", "-o", file_path, "-d", "/Applications"], check=False)
            elif file_path.endswith(".bin"):
                subprocess.run(["chmod", "+x", file_path], check=False)
                subprocess.run([file_path], check=False)
            QMessageBox.information(self, "Done", "✅ StackCheckMate installed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Installation failed:\n{e}")
        finally:
            self.download_btn.setEnabled(True)
            self.label.setText("✅ Installation Complete!")


# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartInstaller()
    window.show()
    sys.exit(app.exec())
