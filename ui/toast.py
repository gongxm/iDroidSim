from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont

class Toast(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)
        self.message = ""
        
    def showMessage(self, message, duration=2000):
        # 输出message
        print(message)
        self.message = message
        # 设置固定宽度
        self.setFixedWidth(400)
        self.setFixedHeight(50)
        
        # 计算位置 - 在父窗口中心
        parent_rect = self.parent().geometry()
        x = parent_rect.width() // 2 - self.width() // 2
        y = parent_rect.height() // 2 - self.height() // 2
        self.move(x, y)
        
        self.show()
        self.timer.start(duration)
        
    def paintEvent(self, event):
        if not self.message:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置半透明黑色背景
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        
        # 设置文字
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(0, 0, self.width(), self.height(), 
                        Qt.AlignmentFlag.AlignCenter, self.message)