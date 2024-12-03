import sys
import os
from GDrive_One_Backup import DriveBackupGUI, QApplication, Qt

def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    window = DriveBackupGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()