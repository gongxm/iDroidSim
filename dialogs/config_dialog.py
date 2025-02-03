from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                            QComboBox, QSpinBox, QFormLayout, QCheckBox)
import subprocess
from ui.toast import Toast
from ui.styled_button import StyledButton
from utils import find_avdmanager

class EmulatorConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加模拟器")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_devices()
        self.load_system_images()
    
    def setup_ui(self):
        """设置界面"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                min-width: 200px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #3498db;
            }
            QCheckBox {
                font-size: 14px;
                color: #2c3e50;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # 添加名称输入
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: Pixel_6_API_33")
        form_layout.addRow("模拟器名称:", self.name_edit)
        
        # 添加设备选择
        self.device_combo = QComboBox()
        form_layout.addRow("设备类型:", self.device_combo)
        
        # 添加系统镜像选择
        self.image_combo = QComboBox()
        form_layout.addRow("系统镜像:", self.image_combo)
        
        # 添加内存大小设置
        self.ram_spin = QSpinBox()
        self.ram_spin.setRange(1024, 8192)
        self.ram_spin.setValue(2048)
        self.ram_spin.setSuffix(" MB")
        self.ram_spin.setSingleStep(512)
        form_layout.addRow("内存大小:", self.ram_spin)
        
        layout.addLayout(form_layout)
        
        # 添加创建后启动的开关
        self.start_switch = QCheckBox("创建后立即启动")
        self.start_switch.setChecked(True)
        layout.addWidget(self.start_switch)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_btn = StyledButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f6fa;
                color: #2c3e50;
                border: 2px solid #dcdde1;
            }
            QPushButton:hover {
                background-color: #dcdde1;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # 确定按钮
        confirm_btn = StyledButton("创建")
        confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(confirm_btn)
        
        layout.addLayout(button_layout)
        
        # 添加 Toast 组件
        self.toast = Toast(self)
    
    def load_devices(self):
        """加载可用设备列表"""
        try:
            avdmanager = find_avdmanager()
            if not avdmanager:
                raise Exception("找不到 avdmanager 工具")
            
            # 获取设备列表
            list_cmd = [avdmanager, 'list', 'device']
            result = subprocess.run(list_cmd, capture_output=True, text=True)
            
            # 解析输出
            current_id = None
            current_name = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if line.startswith('id:'):
                    current_id = line.split('or')[0].split('"')[1]
                elif line.startswith('Name:'):
                    current_name = line.split(':')[1].strip()
                    if current_id and current_name:
                        self.device_combo.addItem(current_name, current_id)
                        current_id = None
                        current_name = None
            
        except Exception as e:
            self.toast.showMessage(f"加载设备列表失败：{str(e)}")
    
    def load_system_images(self):
        """加载已安装的系统镜像"""
        try:
            avdmanager = find_avdmanager()
            if not avdmanager:
                raise Exception("找不到 avdmanager 工具")
            
            # 获取系统镜像列表
            list_cmd = [avdmanager, 'list', 'target']
            result = subprocess.run(list_cmd, capture_output=True, text=True)
            
            # 解析输出
            current_version = None
            current_id = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if line.startswith('id:'):
                    current_id = line.split('or')[0].split('"')[1]
                    current_version = line.split('or')[1].split('"')[1]
                    if current_id and current_version:
                        self.image_combo.addItem(f"Android {current_version}", current_id)
                        current_id = None
                        current_version = None
            
        except Exception as e:
            self.toast.showMessage(f"加载系统镜像失败：{str(e)}") 