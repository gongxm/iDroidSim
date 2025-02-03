from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie

class LoadingDialog(QDialog):
    """加载动画对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置为无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        # 设置模态
        self.setWindowModality(Qt.WindowModality.WindowModal)
        # 设置背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 禁止关闭
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建加载动画标签
        self.loading_label = QLabel()
        self.loading_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.movie = QMovie("icons/loading.gif")
        self.movie.setScaledSize(QSize(200,150))
        self.loading_label.setMovie(self.movie)
        self.loading_label.setFixedSize(200,150)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)
        
        # 完全透明
        self.setStyleSheet("""
            * {
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        self.movie.start()
        
        # 如果有父窗口，居中显示在父窗口中
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
    
    def hideEvent(self, event):
        """隐藏事件"""
        super().hideEvent(event)
        self.movie.stop()
    
    def moveEvent(self, event):
        """移动事件 - 保持在父窗口中心"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            if self.pos() != (x, y):
                self.move(x, y)
        super().moveEvent(event) 