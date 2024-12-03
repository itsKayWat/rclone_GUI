import sys
import os
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QListWidget, 
                            QTextEdit, QProgressBar, QCheckBox, QFileDialog,
                            QMessageBox, QDialog, QTreeWidget, QTreeWidgetItem,
                            QTimeEdit, QComboBox, QSpinBox, QDialogButtonBox, 
                            QFormLayout, QGroupBox, QProgressDialog, QSystemTrayIcon, 
                            QMenu, QAction, QLineEdit, QTabWidget)
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal, QTime, QTimer

class DriveBackupGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rclone Backup Manager")
        self.setMinimumSize(800, 600)
        
        # Initialize variables
        self.destinations = []
        self.backup_threads = []
        self.current_worker = None
        
        # Setup rclone path
        self.setup_rclone_path()
        
        # Initialize UI
        self.init_ui()
        
        # Apply dark emerald theme
        self.apply_dark_theme()

    def apply_dark_theme(self):
        """Apply dark emerald theme to the application"""
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #1a2421;
                color: #e0e0e0;
            }
            QWidget {
                background-color: #1a2421;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #0d503c;
                color: #ffd700;
                border: 1px solid #15755a;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #15755a;
            }
            QPushButton:pressed {
                background-color: #0a3c2d;
            }
            QComboBox {
                background-color: #0d503c;
                color: #ffd700;
                border: 1px solid #15755a;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget, QTextEdit, QTreeWidget {
                background-color: #243832;
                color: #e0e0e0;
                border: 1px solid #15755a;
                border-radius: 4px;
            }
            QCheckBox {
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QProgressBar {
                border: 1px solid #15755a;
                border-radius: 4px;
                text-align: center;
                color: #ffd700;
            }
            QProgressBar::chunk {
                background-color: #0d503c;
            }
            QGroupBox {
                border: 1px solid #15755a;
                border-radius: 4px;
                margin-top: 1em;
                color: #ffd700;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QLineEdit {
                background-color: #243832;
                color: #e0e0e0;
                border: 1px solid #15755a;
                border-radius: 4px;
                padding: 2px 5px;
            }
        """)

    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top buttons layout
        top_buttons = QHBoxLayout()
        self.wizard_btn = QPushButton("Configuration Wizard")
        self.help_btn = QPushButton("Help & About")
        self.wizard_btn.setMinimumHeight(30)
        self.help_btn.setMinimumHeight(30)
        top_buttons.addWidget(self.wizard_btn)
        top_buttons.addWidget(self.help_btn)
        main_layout.addLayout(top_buttons)

        # Source and Destination section
        panels_layout = QHBoxLayout()
        
        # Source Panel
        source_group = QGroupBox("Source")
        source_layout = QVBoxLayout()
        self.folder_list = QListWidget()
        source_layout.addWidget(self.folder_list)
        
        # Source Buttons
        folder_btn_layout = QHBoxLayout()
        self.add_folder_btn = QPushButton("Add Folder")
        self.remove_folder_btn = QPushButton("Remove Folder")
        folder_btn_layout.addWidget(self.add_folder_btn)
        folder_btn_layout.addWidget(self.remove_folder_btn)
        source_layout.addLayout(folder_btn_layout)
        source_group.setLayout(source_layout)
        panels_layout.addWidget(source_group)
        
        # Destination Panel
        dest_group = QGroupBox("Destination")
        dest_layout = QVBoxLayout()
        
        # Remote selection
        remote_layout = QHBoxLayout()
        self.remote_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh")
        self.configure_btn = QPushButton("Configure")
        remote_layout.addWidget(self.remote_combo)
        remote_layout.addWidget(self.refresh_btn)
        remote_layout.addWidget(self.configure_btn)
        dest_layout.addLayout(remote_layout)
        
        dest_group.setLayout(dest_layout)
        panels_layout.addWidget(dest_group)
        
        main_layout.addLayout(panels_layout)

        # Options Group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        self.dry_run = QCheckBox("Dry Run (Test)")
        self.verbose = QCheckBox("Verbose Output")
        self.progress_option = QCheckBox("Show Progress")
        options_layout.addWidget(self.dry_run)
        options_layout.addWidget(self.verbose)
        options_layout.addWidget(self.progress_option)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Operation Buttons
        button_layout = QHBoxLayout()
        self.sync_btn = QPushButton("Sync")
        self.copy_btn = QPushButton("Copy")
        self.move_btn = QPushButton("Move")
        self.check_btn = QPushButton("Check")
        button_layout.addWidget(self.sync_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.move_btn)
        button_layout.addWidget(self.check_btn)
        main_layout.addLayout(button_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Log Group
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # Connect signals
        self.wizard_btn.clicked.connect(self.show_config_wizard)
        self.help_btn.clicked.connect(self.show_help)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.remove_folder_btn.clicked.connect(self.remove_folder)
        self.refresh_btn.clicked.connect(self.load_remotes)
        self.configure_btn.clicked.connect(self.configure_rclone)
        self.sync_btn.clicked.connect(lambda: self.execute_operation('sync'))
        self.copy_btn.clicked.connect(lambda: self.execute_operation('copy'))
        self.move_btn.clicked.connect(lambda: self.execute_operation('move'))
        self.check_btn.clicked.connect(lambda: self.execute_operation('check'))

        # Load initial remotes
        self.load_remotes()

    def setup_rclone_path(self):
        """Setup and verify rclone path"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.rclone_path = os.path.join(
                script_dir,
                'rclone-v1.68.2-windows-amd64',
                'rclone.exe'
            )
            
            if not os.path.exists(self.rclone_path):
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Rclone executable not found at: {self.rclone_path}"
                )
                sys.exit(1)
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to initialize rclone: {str(e)}"
            )
            sys.exit(1)

    def add_folder(self):
        """Add a folder to backup"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_list.addItem(folder)

    def remove_folder(self):
        """Remove selected folder"""
        current_item = self.folder_list.currentItem()
        if current_item:
            self.folder_list.takeItem(self.folder_list.row(current_item))

    def load_remotes(self):
        """Load available rclone remotes"""
        try:
            result = subprocess.run(
                [self.rclone_path, "listremotes"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.remote_combo.clear()
                remotes = result.stdout.splitlines()
                self.remote_combo.addItems(remotes)
                self.log_message("Remotes loaded successfully")
            else:
                raise Exception(result.stderr)
        except Exception as e:
            self.log_error(f"Failed to load remotes: {str(e)}")

    def configure_rclone(self):
        """Configure rclone through GUI instead of terminal"""
        try:
            dialog = RcloneConfigDialog(self.rclone_path, self)
            dialog.exec_()
            # Refresh remotes after configuration
            self.load_remotes()
        except Exception as e:
            self.log_error(f"Configuration failed: {str(e)}")

    def log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def log_error(self, message):
        """Add an error message to the log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] ERROR: {message}")

    def show_help(self):
        """Show help and about information"""
        help_dialog = HelpDialog(self)
        help_dialog.exec_()

    def show_config_wizard(self):
        """Show the configuration wizard"""
        wizard = ConfigWizard(self.rclone_path, self)
        wizard.exec_()
        self.load_remotes()  # Refresh after wizard completes

    def execute_operation(self, operation):
        """Execute rclone operation with error handling"""
        try:
            # Validate selections
            if self.folder_list.count() == 0:
                raise ValueError("Please add at least one source folder")
            
            if not self.remote_combo.currentText():
                raise ValueError("Please select a remote destination")

            # Get selected folders and remote
            source_folders = [
                self.folder_list.item(i).text() 
                for i in range(self.folder_list.count())
            ]
            remote = self.remote_combo.currentText()

            # Prepare command with proper flags
            for source in source_folders:
                cmd = [self.rclone_path]
                
                # Add operation
                cmd.append(operation)
                
                # Add flags based on options
                if self.dry_run.isChecked():
                    cmd.append("--dry-run")
                if self.verbose.isChecked():
                    cmd.append("-v")
                if self.progress_option.isChecked():
                    cmd.append("-P")
                
                # Add source and destination
                cmd.append(source)
                cmd.append(f"{remote}")

                # Hide console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                # Execute command
                self.log_message(f"Starting {operation} operation...")
                self.progress_bar.setVisible(True)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    startupinfo=startupinfo
                )

                # Get output
                output, error = process.communicate()

                if process.returncode == 0:
                    self.log_message(f"{operation.capitalize()} completed successfully")
                    if output:
                        self.log_message(output)
                else:
                    raise Exception(f"Operation failed: {error}")

        except ValueError as ve:
            QMessageBox.warning(self, "Operation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Operation Error", str(e))
            self.log_error(str(e))
        finally:
            self.progress_bar.setVisible(False)

class RcloneConfigDialog(QDialog):
    def __init__(self, rclone_path, parent=None):
        super().__init__(parent)
        self.rclone_path = rclone_path
        self.setWindowTitle("Configure Rclone")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Remote type selection
        type_group = QGroupBox("Remote Type")
        type_layout = QVBoxLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Google Drive",
            "OneDrive",
            "Dropbox",
            "Amazon S3",
            "FTP",
            "SFTP",
            "WebDAV"
        ])
        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Remote name
        name_group = QGroupBox("Remote Name")
        name_layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)

        # Credentials
        creds_group = QGroupBox("Credentials")
        creds_layout = QFormLayout()
        self.client_id = QLineEdit()
        self.client_secret = QLineEdit()
        creds_layout.addRow("Client ID:", self.client_id)
        creds_layout.addRow("Client Secret:", self.client_secret)
        creds_group.setLayout(creds_layout)
        layout.addWidget(creds_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.configure_btn = QPushButton("Configure")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.configure_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        # Connect signals
        self.configure_btn.clicked.connect(self.create_remote)
        self.cancel_btn.clicked.connect(self.reject)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)

    def create_remote(self):
        """Create rclone remote using subprocess with no window"""
        try:
            remote_name = self.name_edit.text()
            remote_type = self.type_combo.currentText().lower().replace(" ", "")
            
            # Prepare configuration command
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            # Create remote
            config_cmd = [
                self.rclone_path,
                "config",
                "create",
                remote_name,
                remote_type,
                f"client_id={self.client_id.text()}",
                f"client_secret={self.client_secret.text()}",
                "--non-interactive"
            ]

            result = subprocess.run(
                config_cmd,
                capture_output=True,
                text=True,
                startupinfo=startupinfo
            )

            if result.returncode == 0:
                QMessageBox.information(self, "Success", f"Remote '{remote_name}' configured successfully")
                self.accept()
            else:
                raise Exception(result.stderr)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to configure remote: {str(e)}")

    def on_type_changed(self, remote_type):
        """Update UI based on selected remote type"""
        # Show/hide relevant fields based on remote type
        is_cloud = remote_type in ["Google Drive", "OneDrive", "Dropbox"]
        self.client_id.setVisible(is_cloud)
        self.client_secret.setVisible(is_cloud)

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help & About")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # About tab
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
            <h2>Rclone Backup Manager</h2>
            <p><b>Created by:</b> Chris Loetz</p>
            <h3>Purpose</h3>
            <p>This tool was created to provide a user-friendly graphical interface for Rclone, 
            making it easier for users to manage their cloud backups without needing to use 
            command-line interfaces.</p>
            <h3>Features</h3>
            <ul>
                <li>Easy-to-use graphical interface</li>
                <li>Support for multiple cloud providers</li>
                <li>Automated backup configuration</li>
                <li>Real-time backup progress monitoring</li>
                <li>Detailed logging and error reporting</li>
            </ul>
        """)
        about_layout.addWidget(about_text)
        tabs.addTab(about_widget, "About")
        
        # Usage Guide tab
        guide_widget = QWidget()
        guide_layout = QVBoxLayout(guide_widget)
        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        guide_text.setHtml("""
            <h2>Quick Start Guide</h2>
            <ol>
                <li><b>Initial Setup:</b>
                    <ul>
                        <li>Click 'Configuration Wizard' in the Help menu</li>
                        <li>Follow the wizard to set up your cloud storage</li>
                        <li>Add folders you want to backup</li>
                    </ul>
                </li>
                <li><b>Adding Backup Sources:</b>
                    <ul>
                        <li>Use 'Add Folder' to select folders for backup</li>
                        <li>Remove unwanted folders with 'Remove Folder'</li>
                    </ul>
                </li>
                <li><b>Backup Operations:</b>
                    <ul>
                        <li>Sync: One-way sync to cloud</li>
                        <li>Copy: Copy files to cloud</li>
                        <li>Move: Move files to cloud</li>
                        <li>Check: Verify backup integrity</li>
                    </ul>
                </li>
            </ol>
        """)
        guide_layout.addWidget(guide_text)
        tabs.addTab(guide_widget, "Usage Guide")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def apply_theme(self):
        """Apply the dark emerald theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2421;
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #243832;
                color: #e0e0e0;
                border: 1px solid #15755a;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0d503c;
                color: #ffd700;
                border: 1px solid #15755a;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QTabWidget::pane {
                border: 1px solid #15755a;
                background-color: #1a2421;
            }
            QTabBar::tab {
                background-color: #0d503c;
                color: #ffd700;
                border: 1px solid #15755a;
                padding: 5px 15px;
            }
            QTabBar::tab:selected {
                background-color: #15755a;
            }
        """)

class ConfigWizard(QDialog):
    def __init__(self, rclone_path, parent=None):
        super().__init__(parent)
        self.rclone_path = rclone_path
        self.setWindowTitle("Backup Configuration Wizard")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Welcome message
        welcome = QLabel(
            "Welcome to the Backup Configuration Wizard!\n\n"
            "This wizard will help you set up your cloud storage providers "
            "and configure your backup settings."
        )
        welcome.setWordWrap(True)
        layout.addWidget(welcome)
        
        # Cloud provider selection
        provider_group = QGroupBox("Select Cloud Provider")
        provider_layout = QVBoxLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "Google Drive",
            "OneDrive",
            "Dropbox",
            "Amazon S3",
            "Box",
            "FTP",
            "SFTP",
            "WebDAV"
        ])
        provider_layout.addWidget(self.provider_combo)
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # Provider-specific settings will be dynamically added here
        self.settings_group = QGroupBox("Provider Settings")
        self.settings_layout = QFormLayout()
        self.settings_group.setLayout(self.settings_layout)
        layout.addWidget(self.settings_group)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        next_btn = QPushButton("Next →")
        finish_btn = QPushButton("Finish")
        button_layout.addWidget(back_btn)
        button_layout.addWidget(next_btn)
        button_layout.addWidget(finish_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.provider_combo.currentTextChanged.connect(self.update_provider_settings)
        back_btn.clicked.connect(self.go_back)
        next_btn.clicked.connect(self.go_next)
        finish_btn.clicked.connect(self.finish_setup)

    def update_provider_settings(self, provider):
        """Update settings form based on selected provider"""
        # Clear existing settings
        while self.settings_layout.count():
            item = self.settings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add common fields
        self.remote_name = QLineEdit()
        self.settings_layout.addRow("Remote Name:", self.remote_name)

        if provider in ["Google Drive", "OneDrive", "Dropbox", "Box"]:
            self.client_id = QLineEdit()
            self.client_secret = QLineEdit()
            self.settings_layout.addRow("Client ID:", self.client_id)
            self.settings_layout.addRow("Client Secret:", self.client_secret)
            
        elif provider == "Amazon S3":
            self.access_key = QLineEdit()
            self.secret_key = QLineEdit()
            self.region = QComboBox()
            self.region.addItems(["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"])
            self.settings_layout.addRow("Access Key:", self.access_key)
            self.settings_layout.addRow("Secret Key:", self.secret_key)
            self.settings_layout.addRow("Region:", self.region)
            
        elif provider in ["FTP", "SFTP"]:
            self.host = QLineEdit()
            self.user = QLineEdit()
            self.password = QLineEdit()
            self.password.setEchoMode(QLineEdit.Password)
            self.port = QSpinBox()
            self.port.setRange(1, 65535)
            self.port.setValue(22 if provider == "SFTP" else 21)
            
            self.settings_layout.addRow("Host:", self.host)
            self.settings_layout.addRow("User:", self.user)
            self.settings_layout.addRow("Password:", self.password)
            self.settings_layout.addRow("Port:", self.port)

    def create_remote(self):
        """Create rclone remote based on current settings"""
        try:
            provider = self.provider_combo.currentText()
            remote_name = self.remote_name.text()
            
            if not remote_name:
                raise ValueError("Remote name is required")

            # Hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            # Base command
            cmd = [
                self.rclone_path,
                "config",
                "create",
                remote_name,
                provider.lower().replace(" ", "")
            ]

            # Add provider-specific parameters
            if provider in ["Google Drive", "OneDrive", "Dropbox", "Box"]:
                cmd.extend([
                    f"client_id={self.client_id.text()}",
                    f"client_secret={self.client_secret.text()}"
                ])
            
            elif provider == "Amazon S3":
                cmd.extend([
                    f"access_key_id={self.access_key.text()}",
                    f"secret_access_key={self.secret_key.text()}",
                    f"region={self.region.currentText()}"
                ])
                
            elif provider in ["FTP", "SFTP"]:
                cmd.extend([
                    f"host={self.host.text()}",
                    f"user={self.user.text()}",
                    f"pass={self.password.text()}",
                    f"port={self.port.value()}"
                ])

            # Run configuration command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                startupinfo=startupinfo
            )

            if result.returncode == 0:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Remote '{remote_name}' configured successfully!"
                )
                return True
            else:
                raise Exception(result.stderr)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Configuration Error",
                f"Failed to configure remote: {str(e)}"
            )
            return False

    def validate_current_page(self):
        """Validate the current page before proceeding"""
        try:
            provider = self.provider_combo.currentText()
            
            if not self.remote_name.text():
                raise ValueError("Remote name is required")

            if provider in ["Google Drive", "OneDrive", "Dropbox", "Box"]:
                if not self.client_id.text() or not self.client_secret.text():
                    raise ValueError("Client ID and Secret are required")
                    
            elif provider == "Amazon S3":
                if not self.access_key.text() or not self.secret_key.text():
                    raise ValueError("Access Key and Secret Key are required")
                    
            elif provider in ["FTP", "SFTP"]:
                if not self.host.text() or not self.user.text() or not self.password.text():
                    raise ValueError("Host, User, and Password are required")

            return True

        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return False

    def go_next(self):
        """Proceed to next step"""
        if self.validate_current_page():
            if self.create_remote():
                self.accept()

    def go_back(self):
        """Return to previous step"""
        self.reject()

    def finish_setup(self):
        """Complete the wizard"""
        if self.validate_current_page():
            if self.create_remote():
                self.accept()

    def apply_theme(self):
        """Apply dark emerald theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a2421;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #15755a;
                border-radius: 4px;
                margin-top: 1em;
                color: #ffd700;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #243832;
                color: #e0e0e0;
                border: 1px solid #15755a;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0d503c;
                color: #ffd700;
                border: 1px solid #15755a;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #15755a;
            }
        """)

def main():
    # Hide terminal window on Windows
    if sys.platform.startswith('win'):
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)

    app = QApplication(sys.argv)
    window = DriveBackupGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()