from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie

class LoadingDialog(QDialog):
    """加载动画对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setFixedSize(200,150)
        
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
        
        # 居中显示
        parent_rect = self.parent().geometry()
        x = parent_rect.center().x() - self.width() // 2
        y = parent_rect.center().y() - self.height() // 2
        self.move(x, y)
    
    def hideEvent(self, event):
        """隐藏事件"""
        super().hideEvent(event)
        self.movie.stop() 