import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from emulator_manager import EmulatorManager

def main():
    app = QApplication(sys.argv)
     # 设置 Dock 图标
    app.setWindowIcon(QIcon("icons/app.icns"))
    window = EmulatorManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 