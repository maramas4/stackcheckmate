# ===============================================================
# StackCheckMate - Universal Developer Toolkit
# Product of Quick Red Tech
# Owned by Chisom Life Eke
# Version: 1.2.0
# ===============================================================

import sys, subprocess, platform, os, json, psutil, threading, time
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QMessageBox, QMenuBar, QMenu,
    QHBoxLayout, QInputDialog, QTabWidget, QScrollArea, QFormLayout
)
from PySide6.QtGui import QAction, QFont, QIcon, QKeySequence
from PySide6.QtCore import Qt
from plyer import notification


class StackCheckMate(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StackCheckMate - Universal Dev Toolkit")
        self.setGeometry(200, 150, 840, 720)
        self.setStyleSheet(self.main_style())
        self.setWindowIcon(QIcon("icon.png"))
        self.profile_file = "profile.json"
        self.init_ui()

        # Start motivational notifier in background
        threading.Thread(target=self.motivation_thread, daemon=True).start()

    # --------------------------- UI SETUP --------------------------
    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab {background:#1a1a1a; color:white; padding:10px;} "
                                "QTabBar::tab:selected {background:#ff3b3b;}")

        self.tabs.addTab(self.create_installer_tab(), "📦 Package Manager")
        self.tabs.addTab(self.create_env_tab(), "🌍 Env & System Info")
        self.tabs.addTab(self.create_network_tab(), "🌐 Network Monitor")
        self.tabs.addTab(self.create_profile_tab(), "👨‍💻 Dev Profile")

        self.setCentralWidget(self.tabs)
        self.setMenuBar(self.create_menu())

    def create_menu(self):
        menubar = QMenuBar(self)
        menubar.setStyleSheet(self.menu_style())

        file_menu = QMenu("File", self)
        help_menu = QMenu("Help", self)

        menubar.addMenu(file_menu)
        menubar.addMenu(help_menu)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        doc_action = QAction("Documentation", self)
        doc_action.triggered.connect(self.show_docs)
        help_menu.addAction(doc_action)

        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)

        about_action = QAction("About StackCheckMate", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        credits_action = QAction("Credits", self)
        credits_action.triggered.connect(self.show_credits)
        help_menu.addAction(credits_action)

        return menubar

    # -------------------- PAGE 1: PACKAGE MANAGER -------------------
    def create_installer_tab(self):
        widget = QWidget()
        scroll = QScrollArea()
        layout = QVBoxLayout(widget)

        title = QLabel("⚙️ StackCheckMate - Package Installer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 22, QFont.Bold))
        title.setStyleSheet("color:#ff3b3b; margin:15px;")
        layout.addWidget(title)

        label_pkg = QLabel("🔧 Select Language:")
        label_pkg.setStyleSheet("color:white; font-weight:bold; font-size:15px;")
        layout.addWidget(label_pkg)

        self.language_select = QComboBox()
        self.language_select.addItems(["Python (pip)", "Node.js (npm)", "Java (JDK)", "Ruby (gem)"])
        self.language_select.setStyleSheet(self.combo_style())
        layout.addWidget(self.language_select)

        self.package_input = QLineEdit()
        self.package_input.setPlaceholderText("Enter package name(s), comma separated")
        self.package_input.setStyleSheet(self.input_style())
        layout.addWidget(self.package_input)

        install_btn = QPushButton("🚀 Install Package(s)")
        install_btn.setStyleSheet(self.button_style())
        install_btn.setShortcut(QKeySequence("Ctrl+I"))
        install_btn.clicked.connect(self.install_packages)
        layout.addWidget(install_btn)

        label_inst = QLabel("📦 Installed Packages:")
        label_inst.setStyleSheet("color:white; font-weight:bold; margin-top:10px; font-size:15px;")
        layout.addWidget(label_inst)

        self.installed_packages_btn = QPushButton("Show Installed Packages")
        self.installed_packages_btn.setStyleSheet(self.button_style())
        self.installed_packages_btn.clicked.connect(self.show_installed_packages)
        layout.addWidget(self.installed_packages_btn)

        self.installed_packages_text = QTextEdit()
        self.installed_packages_text.setReadOnly(True)
        self.installed_packages_text.setStyleSheet(self.textedit_style())
        layout.addWidget(self.installed_packages_text)

        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        return scroll

    # ------------------ PAGE 2: ENV VARIABLES -----------------------
    def create_env_tab(self):
        widget = QWidget()
        scroll = QScrollArea()
        layout = QVBoxLayout(widget)

        label_env = QLabel("🌍 System Environment Variables:")
        label_env.setStyleSheet("color:white; font-weight:bold; font-size:15px;")
        layout.addWidget(label_env)

        btn_row = QHBoxLayout()
        env_btn = QPushButton("Show Variables")
        env_btn.setStyleSheet(self.button_style())
        env_btn.setShortcut(QKeySequence("Ctrl+E"))
        env_btn.clicked.connect(self.show_env_variables)
        btn_row.addWidget(env_btn)

        add_env_btn = QPushButton("➕ Add / Edit Variable")
        add_env_btn.setStyleSheet(self.button_style())
        add_env_btn.clicked.connect(self.add_edit_env)
        btn_row.addWidget(add_env_btn)

        del_env_btn = QPushButton("🗑️ Delete Variable")
        del_env_btn.setStyleSheet(self.button_style())
        del_env_btn.clicked.connect(self.delete_env)
        btn_row.addWidget(del_env_btn)

        layout.addLayout(btn_row)

        self.env_text = QTextEdit()
        self.env_text.setReadOnly(True)
        self.env_text.setStyleSheet(self.textedit_style())
        layout.addWidget(self.env_text)

        label_info = QLabel("💻 System Info:")
        label_info.setStyleSheet("color:white; font-weight:bold; margin-top:10px; font-size:15px;")
        layout.addWidget(label_info)

        self.os_info_label = QLabel(f"OS: {platform.system()} | Version: {platform.version()}")
        self.os_info_label.setStyleSheet("color:#ccc; font-size:13px;")
        layout.addWidget(self.os_info_label)

        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        return scroll

    # ------------------ PAGE 3: NETWORK MONITOR ---------------------
    def create_network_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("🌐 Real-Time Network Monitor")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 20, QFont.Bold))
        title.setStyleSheet("color:#ff3b3b; margin:10px;")
        layout.addWidget(title)

        self.net_label = QLabel("Checking network...")
        self.net_label.setStyleSheet("color:#00ffcc; font-size:14px;")
        layout.addWidget(self.net_label)

        refresh_btn = QPushButton("🔄 Refresh Now")
        refresh_btn.setStyleSheet(self.button_style())
        refresh_btn.clicked.connect(self.update_network_usage)
        layout.addWidget(refresh_btn)

        threading.Thread(target=self.auto_refresh_network, daemon=True).start()
        return widget

    def auto_refresh_network(self):
        while True:
            self.update_network_usage()
            time.sleep(5)

    def update_network_usage(self):
        counters = psutil.net_io_counters()
        sent = round(counters.bytes_sent / (1024 * 1024), 2)
        recv = round(counters.bytes_recv / (1024 * 1024), 2)
        self.net_label.setText(f"📡 Upload: {sent} MB | Download: {recv} MB")

    # ------------------ PAGE 4: PROFILE -------------------
    def create_profile_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setLabelAlignment(Qt.AlignLeft)
        layout.setFormAlignment(Qt.AlignTop)

        self.name_input = QLineEdit()
        self.github_input = QLineEdit()
        self.linkedin_input = QLineEdit()
        self.email_input = QLineEdit()
        self.twitter_input = QLineEdit()
        self.whatsapp_input = QLineEdit()
        self.facebook_input = QLineEdit()

        for field in [self.name_input, self.github_input, self.linkedin_input,
                      self.email_input, self.twitter_input, self.whatsapp_input, self.facebook_input]:
            field.setStyleSheet(self.input_style())

        layout.addRow("👤 Full Name:", self.name_input)
        layout.addRow("💻 GitHub:", self.github_input)
        layout.addRow("🔗 LinkedIn:", self.linkedin_input)
        layout.addRow("📧 Email:", self.email_input)
        layout.addRow("🐦 Twitter:", self.twitter_input)
        layout.addRow("📱 WhatsApp:", self.whatsapp_input)
        layout.addRow("📘 Facebook:", self.facebook_input)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("💾 Save Profile")
        save_btn.setStyleSheet(self.button_style())
        save_btn.setShortcut(QKeySequence("Ctrl+S"))
        save_btn.clicked.connect(self.save_profile)
        btn_row.addWidget(save_btn)

        view_btn = QPushButton("👁️ Preview Card")
        view_btn.setStyleSheet(self.button_style())
        view_btn.clicked.connect(self.preview_profile)
        btn_row.addWidget(view_btn)

        layout.addRow(btn_row)
        self.load_profile()
        return widget

    # ---------------------- DOCS + INFO POPUPS ----------------------
    def show_docs(self):
        msg = (
            "📘 StackCheckMate Documentation\n\n"
            "• 📦 Package Manager: Install & view packages for Python, Node, Ruby, Java.\n"
            "• 🌍 Env & System Info: View and edit your environment variables.\n"
            "• 🌐 Network Monitor: See your system's real-time network stats.\n"
            "• 👨‍💻 Dev Profile: Store your developer info card locally.\n"
            "• 🔔 Motivation: Random dev quotes pop up every few hours.\n\n"
            "Use the menu bar or keyboard shortcuts to move faster."
        )
        QMessageBox.information(self, "Documentation", msg)

    def show_shortcuts(self):
        msg = (
            "⌨️ Keyboard Shortcuts:\n\n"
            "Ctrl + I → Install Package(s)\n"
            "Ctrl + E → Show Environment Variables\n"
            "Ctrl + S → Save Profile\n"
            "Ctrl + Q → Exit Application"
        )
        QMessageBox.information(self, "Keyboard Shortcuts", msg)

    def show_credits(self):
        QMessageBox.information(
            self, "Credits",
            "Developed by Quick Red Tech\n"
            "Lead Developer: Chisom Life Eke\n"
            "UI Framework: PySide6 (Qt for Python)\n"
            "Special Thanks: Raymond ProGuy for inspiration!"
        )

    def show_about(self):
        QMessageBox.information(
            self, "About StackCheckMate",
            "⚙️ StackCheckMate v1.2.0\n\nA Universal Developer Toolkit for managing packages, "
            "environment variables, and system monitoring.\n\n"
            "Built by Quick Red Tech.\nOwned by Chisom Life Eke.\n"
            "Theme: Red | Neon | Black | White."
        )

    # ----------------------- REST OF LOGIC (same) --------------------
    def motivation_thread(self):
        while True:
            try:
                name = "Developer"
                if os.path.exists(self.profile_file):
                    with open(self.profile_file, "r") as f:
                        data = json.load(f)
                        name = data.get("name", "Developer")
                notification.notify(
                    title="💪 Keep Grinding!",
                    message=f"Hey {name}, remember — consistency creates legends. 🚀",
                    timeout=10
                )
            except Exception:
                pass
            time.sleep(7200)

    def save_profile(self):
        data = {
            "name": self.name_input.text(),
            "github": self.github_input.text(),
            "linkedin": self.linkedin_input.text(),
            "email": self.email_input.text(),
            "twitter": self.twitter_input.text(),
            "whatsapp": self.whatsapp_input.text(),
            "facebook": self.facebook_input.text()
        }
        with open(self.profile_file, "w") as f:
            json.dump(data, f, indent=4)
        QMessageBox.information(self, "Saved", "Profile saved successfully!")

    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, "r") as f:
                data = json.load(f)
                self.name_input.setText(data.get("name", ""))
                self.github_input.setText(data.get("github", ""))
                self.linkedin_input.setText(data.get("linkedin", ""))
                self.email_input.setText(data.get("email", ""))
                self.twitter_input.setText(data.get("twitter", ""))
                self.whatsapp_input.setText(data.get("whatsapp", ""))
                self.facebook_input.setText(data.get("facebook", ""))

    def preview_profile(self):
        name = self.name_input.text() or "Unknown Dev"
        card = (
            f"👤 {name}\n"
            f"💻 GitHub: {self.github_input.text()}\n"
            f"🔗 LinkedIn: {self.linkedin_input.text()}\n"
            f"🐦 Twitter: {self.twitter_input.text()}\n"
            f"📧 Email: {self.email_input.text()}\n"
            f"📱 WhatsApp: {self.whatsapp_input.text()}\n"
            f"📘 Facebook: {self.facebook_input.text()}"
        )
        QMessageBox.information(self, "Profile Card", card)

    def show_about(self):
        QMessageBox.information(
            self, "About StackCheckMate",
            "⚙️ StackCheckMate\n\nA Universal Developer Toolkit for managing packages, "
            "environment variables, and network usage.\n\nBuilt by Quick Red Tech.\n"
            "Owned by Chisom Life Eke.\nTheme: Red | Neon | Black | White."
        )

    # --------------- Package & Env logic kept from base version ---------------
    def install_packages(self):
        lang = self.language_select.currentText()
        packages = [p.strip() for p in self.package_input.text().split(",") if p.strip()]
        if not packages:
            QMessageBox.warning(self, "Error", "Please enter at least one package name.")
            return
        try:
            if "Python" in lang:
                for pkg in packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            elif "Node" in lang:
                for pkg in packages:
                    subprocess.check_call(["npm", "install", "-g", pkg])
            elif "Java" in lang:
                QMessageBox.information(self, "Info", "For Java JDK, use SDKMAN or system manager.")
            elif "Ruby" in lang:
                for pkg in packages:
                    subprocess.check_call(["gem", "install", pkg])
            QMessageBox.information(self, "Success", "Package(s) installed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_installed_packages(self):
        lang = self.language_select.currentText()
        try:
            if "Python" in lang:
                out = subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode()
            elif "Node" in lang:
                out = subprocess.check_output(["npm", "list", "-g", "--depth=0"]).decode()
            elif "Java" in lang:
                out = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT).decode()
            elif "Ruby" in lang:
                out = subprocess.check_output(["gem", "list"]).decode()
            self.installed_packages_text.setPlainText(out)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_env_variables(self):
        env_vars = "\n".join([f"{k}={v}" for k, v in os.environ.items()])
        self.env_text.setPlainText(env_vars)

    def add_edit_env(self):
        key, ok1 = QInputDialog.getText(self, "Add/Edit Variable", "Enter variable name:")
        if not ok1 or not key:
            return
        value, ok2 = QInputDialog.getText(self, "Add/Edit Variable", f"Enter value for {key}:")
        if not ok2:
            return
        try:
            self.set_env_variable(key, value)
            QMessageBox.information(self, "Success", f"Variable {key} set successfully.")
            self.show_env_variables()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_env(self):
        key, ok = QInputDialog.getText(self, "Delete Variable", "Enter variable name to delete:")
        if not ok or not key:
            return
        try:
            os.environ.pop(key, None)
            if platform.system() == "Windows":
                subprocess.run(["setx", key, ""], shell=True)
            QMessageBox.information(self, "Deleted", f"Variable '{key}' removed.")
            self.show_env_variables()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def set_env_variable(self, key, value):
        sysname = platform.system()
        os.environ[key] = value
        if sysname == "Windows":
            subprocess.run(["setx", key, value], shell=True)
        elif sysname == "Linux":
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write(f'\nexport {key}="{value}"\n')
        elif sysname == "Darwin":
            with open(os.path.expanduser("~/.zshrc"), "a") as f:
                f.write(f'\nexport {key}="{value}"\n')

    # --------------------------- STYLES -----------------------------
    def main_style(self):
        return "QMainWindow {background-color:#0d0d0d;}"

    def button_style(self):
        return """QPushButton {
            background-color:#ff3b3b; color:white; font-weight:bold;
            padding:10px; border-radius:8px;}
            QPushButton:hover {background-color:#ff5c5c; border:1px solid white;}"""

    def combo_style(self):
        return """QComboBox {
            background-color:#1a1a1a; color:white; padding:6px;
            border:1px solid #ff3b3b; border-radius:5px;}"""

    def input_style(self):
        return """QLineEdit {
            background-color:#1a1a1a; color:white; padding:7px;
            border:1px solid #ff3b3b; border-radius:5px;}"""

    def textedit_style(self):
        return """QTextEdit {
            background-color:#0f0f0f; color:#00ffcc;
            border:1px solid #ff3b3b; border-radius:6px; padding:5px;}"""

    def menu_style(self):
        return """QMenuBar {background-color:#1a1a1a; color:white;}
            QMenuBar::item:selected {background-color:#ff3b3b;}
            QMenu {background-color:#1a1a1a; color:white;}
            QMenu::item:selected {background-color:#ff3b3b;}"""


# ----------------------------- RUN APP -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ================= TERMS & WARNINGS ==================
    warning_text = (
        "⚠️  IMPORTANT NOTICE - READ BEFORE CONTINUING\n\n"
        "Welcome to StackCheckMate v1.2.1\n"
        "A Universal Developer Toolkit created by Quick Red Tech.\n"
        "Owned by: Chisom Life Eke.\n\n"
        "By using this software, you agree to the following terms:\n\n"
        "1️⃣ You are responsible for all package installations and system modifications made with this tool.\n"
        "2️⃣ StackCheckMate will not be liable for data loss, environment corruption, or dependency conflicts.\n"
        "3️⃣ On Linux/macOS, added environment variables may require restarting your terminal or PC.\n"
        "4️⃣ Admin/root privileges may be required for some package installations (e.g., npm global installs).\n"
        "5️⃣ Notifications are safe and local — no data is sent externally.\n\n"
        "✅ This toolkit is intended for educational, personal, and development purposes only.\n"
        "⚙️ By clicking 'I Understand & Agree', you acknowledge full responsibility for its use.\n\n"
        "Developed by Quick Red Tech © 2025 | All Rights Reserved."
    )

    msg = QMessageBox()
    msg.setWindowTitle("⚠️ StackCheckMate - Terms & Warning")
    msg.setText(warning_text)
    msg.setIcon(QMessageBox.Warning)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Ok)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #0d0d0d;
            color: white;
            font-family: Consolas;
            font-size: 13px;
        }
        QPushButton {
            background-color: #ff3b3b;
            color: white;
            font-weight: bold;
            padding: 8px 14px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #ff5c5c;
        }
    """)

    user_choice = msg.exec()

    if user_choice == QMessageBox.Ok:
        # Continue to app
        window = StackCheckMate()
        window.show()
        sys.exit(app.exec())
    else:
        # Exit app if user disagrees
        print("User declined the terms. Closing application...")
        sys.exit(0)