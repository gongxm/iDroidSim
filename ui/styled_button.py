from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
class StyledButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))  # 减小图标尺寸
        self.setMinimumHeight(35)  # 调整最小高度
        self.setCursor(Qt.CursorShape.PointingHandCursor)