import subprocess
import os

from PyQt6.QtWidgets import ( QMainWindow, QWidget, QVBoxLayout, QListWidget, QMessageBox, QHBoxLayout,
                            QLabel, QListWidgetItem, QDialog, QFormLayout, 
                            QLineEdit, QComboBox, QDialogButtonBox, QSpinBox, QProgressDialog,
                            QAbstractButton)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QIcon

# 修改为绝对导入
from ui.toast import Toast
from ui.styled_button import StyledButton
from dialogs.environment_dialog import EnvironmentDialog
from dialogs.image_manager_dialog import ImageManagerDialog
from utils import find_avdmanager,EMULATOR_PATH
from dialogs.config_dialog import EmulatorConfigDialog
from ui.loading_dialog import LoadingDialog



class EmulatorListItem(QWidget):
    """模拟器列表项组件"""
    def __init__(self, name, status, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 名称和状态标签
        info = QLabel(f"{name} {status}")
        info.setStyleSheet("font-size: 14px; color: #2c3e50;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        # 添加控制按钮
        if "运行中" in status:
            # 运行中只显示停止按钮
            stop_btn = StyledButton("停止", "icons/stop.png")
            stop_btn.setObjectName("stop-btn")
            stop_btn.clicked.connect(lambda: parent.stop_emulator(name))
            layout.addWidget(stop_btn)
        else:
            # 未运行时显示启动和删除按钮
            start_btn = StyledButton("启动", "icons/start.png")
            start_btn.clicked.connect(lambda: parent.start_emulator(name))
            layout.addWidget(start_btn)
            
            delete_btn = StyledButton("删除", "icons/delete.png")
            delete_btn.setObjectName("delete-btn")
            delete_btn.clicked.connect(lambda: parent.delete_emulator(name))
            layout.addWidget(delete_btn)

class QSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(True)
        self.setFixedSize(36, 18)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        if self.isChecked():
            painter.setBrush(QColor("#2ecc71"))
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            painter.setBrush(QColor("#dcdde1"))
            painter.setPen(Qt.PenStyle.NoPen)
        
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 9, 9)
        
        # 绘制滑块
        if self.isChecked():
            painter.setBrush(QColor("white"))
            painter.drawEllipse(18, 1, 16, 16)
        else:
            painter.setBrush(QColor("white"))
            painter.drawEllipse(2, 1, 16, 16)

class LoadDeviceImagesThread(QThread):
    """加载设备和系统镜像的线程"""
    devices_loaded = pyqtSignal(list)  # 发送设备列表
    images_loaded = pyqtSignal(list)  # 发送系统镜像列表
    error = pyqtSignal(str)  # 发送错误信息
    
    def run(self):
        try:
            # 加载设备列表
            avdmanager = find_avdmanager()
            if not avdmanager:
                raise Exception("找不到 avdmanager 工具")
            
            # 使用 avdmanager 获取设备列表
            cmd = [avdmanager, 'list', 'device']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 解析输出获取设备列表
            current_device = {}
            devices = []
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('id:'):
                    if current_device:
                        devices.append(current_device)
                    device_id = line.split('id: ')[1].strip()
                    if ' or ' in device_id:
                        device_id = device_id.split(' or ')[0].strip()
                    current_device = {'id': device_id}
                elif line.startswith('Name:') and current_device:
                    name = line.split('Name: ')[1].strip()
                    if ' or ' in name:
                        name = name.split(' or ')[0].strip()
                    current_device['name'] = name
            
            if current_device:
                devices.append(current_device)
            
            # 如果没有找到设备，使用默认设备列表
            if not devices:
                devices = [
                    {"name": "Pixel 6", "id": "pixel_6"},
                    {"name": "Pixel 5", "id": "pixel_5"},
                    {"name": "Pixel 4", "id": "pixel_4"},
                    {"name": "Pixel 3", "id": "pixel_3"},
                    {"name": "Pixel 2", "id": "pixel_2"},
                    {"name": "Pixel", "id": "pixel"},
                    {"name": "Nexus 6P", "id": "Nexus_6P"},
                    {"name": "Nexus 6", "id": "Nexus_6"},
                    {"name": "Nexus 5", "id": "Nexus_5"},
                    {"name": "Pixel C", "id": "pixel_c"},
                    {"name": "Nexus 9", "id": "Nexus_9"},
                    {"name": "Nexus 7", "id": "Nexus_7_2013"}
                ]
            
            self.devices_loaded.emit(devices)
            
            # 加载系统镜像
            sdkmanager = os.path.join(os.path.dirname(find_avdmanager()), 'sdkmanager')
            if not os.path.exists(sdkmanager):
                raise Exception("找不到 sdkmanager 工具")
            
            # 获取已安装镜像
            cmd = [sdkmanager, '--list_installed']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 解析输出获取系统镜像
            images = []
            for line in result.stdout.split('\n'):
                if 'system-images;android-' in line:
                    try:
                        parts = line.strip().split('|')[0].strip().split(';')
                        version = parts[1].replace('android-', '')
                        image_type = parts[2]
                        arch = parts[3]
                        
                        images.append({
                            'version': version,
                            'type': image_type,
                            'arch': arch,
                            'full_name': f'system-images;android-{version};{image_type};{arch}'
                        })
                    except:
                        continue
            
            # 按版本号从大到小排序
            images.sort(key=lambda x: -int(x['version'].split('-')[0]))
            
            self.images_loaded.emit(images)
            
        except Exception as e:
            self.error.emit(str(e))

class EmulatorConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加模拟器")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                min-width: 100px;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 10px;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                background-color: white;
                min-width: 250px;
                min-height: 20px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #54a0ff;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: url(icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                selection-background-color: white;
                selection-color: #ff6b6b;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                min-height: 24px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: white;
                color: #ff6b6b;
            }
            QPushButton {
                padding: 10px 25px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton[text="OK"] {
                background-color: #2ecc71;
                color: white;
                border: none;
            }
            QPushButton[text="OK"]:hover {
                background-color: #27ae60;
            }
            QPushButton[text="Cancel"] {
                background-color: #f5f6fa;
                color: #2c3e50;
                border: 2px solid #dcdde1;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #dcdde1;
            }
            QFormLayout {
                spacing: 20px;
            }
        """)
        
        layout = QFormLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 模拟器名称
        name_label = QLabel("模拟器名称:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入模拟器名称")
        layout.addRow(name_label, self.name_edit)
        
        # 设备类型
        device_label = QLabel("设备类型:")
        self.device_combo = QComboBox()
        layout.addRow(device_label, self.device_combo)
        
        # 系统镜像
        image_label = QLabel("系统镜像:")
        self.image_combo = QComboBox()
        layout.addRow(image_label, self.image_combo)
        
        # 内存大小
        ram_label = QLabel("内存大小:")
        self.ram_spin = QSpinBox()
        self.ram_spin.setRange(1024, 8192)
        self.ram_spin.setValue(2048)
        self.ram_spin.setSingleStep(1024)
        self.ram_spin.setSuffix(" MB")
        self.ram_spin.setDisplayIntegerBase(10)
        layout.addRow(ram_label, self.ram_spin)
        
        # 添加启动开关
        start_label = QLabel("创建后启动:")
        start_layout = QHBoxLayout()
        self.start_switch = QSwitch()
        self.start_switch.setChecked(True)  # 默认选中
        
        # 添加是/否标签
        start_layout.addWidget(self.start_switch)
        self.status_label = QLabel("是")
        self.status_label.setStyleSheet("""
            color: #2ecc71;
            font-weight: bold;
            font-size: 14px;
            margin-left: 8px;
        """)
        start_layout.addWidget(self.status_label)
        start_layout.addStretch()
        
        # 连接信号
        self.start_switch.toggled.connect(self.on_switch_changed)
        
        layout.addRow(start_label, start_layout)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 添加一个水平布局来居中按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(button_box)
        button_layout.addStretch()
        
        layout.addRow("", button_layout)
        
   
        
        # 添加 Toast 组件
        self.toast = Toast(self)
        
        # 添加加载线程属性
        self.load_thread = None
    
    def accept(self):
        """确认按钮点击事件"""
        # 验证模拟器名称
        if not self.name_edit.text().strip():
            self.toast.showMessage("请输入模拟器名称")
            self.name_edit.setFocus()
            return
        
        # 验证通过，调用父类的 accept 方法关闭对话框
        super().accept()
    
    def showEvent(self, event):
        """对话框显示事件"""
        super().showEvent(event)
        
        # 清空并设置初始状态
        self.device_combo.clear()
        self.image_combo.clear()
        
        # 添加加载提示并禁用下拉框
        self.device_combo.addItem("数据加载中...")
        self.image_combo.addItem("数据加载中...")
        self.device_combo.setEnabled(False)
        self.image_combo.setEnabled(False)
        
        # 开始加载数据
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        # 创建并启动加载线程
        self.load_thread = LoadDeviceImagesThread()
        self.load_thread.devices_loaded.connect(self.handle_devices_loaded)
        self.load_thread.images_loaded.connect(self.handle_images_loaded)
        self.load_thread.error.connect(self.handle_load_error)
        self.load_thread.start()
    
    def handle_devices_loaded(self, devices):
        """处理设备列表加载完成"""
        self.device_combo.clear()
        for device in devices:
            if 'id' in device and 'name' in device:
                self.device_combo.addItem(device['name'], device['id'])
        self.device_combo.setEnabled(True)
    
    def handle_images_loaded(self, images):
        """处理系统镜像加载完成"""
        self.image_combo.clear()
        if images:
            for image in images:
                display_text = f"Android {image['version']} ({image['type']}, {image['arch']})"
                self.image_combo.addItem(display_text, image['full_name'])
            self.image_combo.setEnabled(True)
        else:
            self.image_combo.addItem("未找到系统镜像")
    
    def handle_load_error(self, error_msg):
        """处理加载错误"""
        self.device_combo.clear()
        self.image_combo.clear()
        self.device_combo.addItem(f"加载失败: {error_msg}")
        self.image_combo.addItem(f"加载失败: {error_msg}")

    def on_switch_changed(self, checked):
        """处理开关状态改变"""
        if checked:
            self.status_label.setText("是")
            self.status_label.setStyleSheet("""
                color: #2ecc71;
                font-weight: bold;
                font-size: 14px;
                margin-left: 8px;
            """)
        else:
            self.status_label.setText("否")
            self.status_label.setStyleSheet("""
                color: #95a5a6;
                font-weight: bold;
                font-size: 14px;
                margin-left: 8px;
            """)

class DownloadProgressDialog(QProgressDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("下载进度")
        self.setMinimumWidth(400)
        self.setMinimumDuration(0)  # 立即显示
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setAutoClose(True)
        self.setAutoReset(True)
        
        # 设置样式
        self.setStyleSheet("""
            QProgressDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                padding: 10px;
            }
            QProgressBar {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                text-align: center;
                background-color: #f5f6fa;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                background-color: #f5f6fa;
                color: #2c3e50;
                border: 2px solid #dcdde1;
            }
            QPushButton:hover {
                background-color: #dcdde1;
            }
        """)


class EmulatorListThread(QThread):
    """加载模拟器列表的线程"""
    finished = pyqtSignal(list, list)  # 发送 (模拟器列表, 运行中的模拟器列表)
    error = pyqtSignal(str)  # 发送错误信息
    
    def run(self):
        try:
            # 获取模拟器列表
            result = subprocess.run([EMULATOR_PATH, '-list-avds'], 
                                 capture_output=True, text=True)
            emulators = [emu for emu in result.stdout.strip().split('\n') if emu]
            
            # 获取正在运行的模拟器
            ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            running_processes = ps_result.stdout.strip().split('\n')
            
            # 检查每个模拟器是否在运行
            running_emulators = []
            for process in running_processes:
                if 'qemu-system-' in process:
                    avd_parts = process.split('-avd ')
                    if len(avd_parts) > 1:
                        emu_part = avd_parts[1].split(' -')[0]
                        emu_name = emu_part.strip()
                        if emu_name in emulators:
                            running_emulators.append(emu_name)
            
            self.finished.emit(emulators, running_emulators)
            
        except Exception as e:
            self.error.emit(str(e))

class EmulatorManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 添加加载动画对话框
        self.loading = LoadingDialog(self)
        
        # 添加加载线程属性
        self.load_thread = None
        
        # 初始化界面
        self.setup_ui()
        
        # 检查环境
        self.check_environment()
        
        # 刷新模拟器列表
        self.refresh_emulators()
    
    def setup_ui(self):
        """设置界面"""
        # 设置应用图标
        self.setWindowIcon(QIcon("icons/app.icns"))
        self.setWindowTitle("Android Emulator")
        self.setGeometry(500, 300, 800, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                border-radius: 5px;
                padding: 0px;
                margin: 0;
                min-height: 54px;
            }
            QListWidget::item:selected {
                background-color: transparent;
                color: #2c3e50;
            }
            QListWidget::item:hover {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2f3542;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton#stop-btn {
                background-color: #ff6b6b;
            }
            QPushButton#stop-btn:hover {
                background-color: #ee5253;
            }
            QPushButton#delete-btn {
                background-color: #ff6b6b;
            }
            QPushButton#delete-btn:hover {
                background-color: #ee5253;
            }
            QStatusBar {
                background-color: white;
                color: #2f3542;
            }
        """)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 在标题行添加镜像管理按钮
        header = QHBoxLayout()
        title = QLabel("Android Emulator")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.addWidget(title)
        
        header.addStretch()

          
        # 添加环境管理按钮
        env_btn = StyledButton("环境管理", "icons/settings.png")
        env_btn.clicked.connect(self.show_environment_dialog)
        header.addWidget(env_btn)

        
        # 添加镜像管理按钮
        image_btn = StyledButton("镜像管理", "icons/image.png")
        image_btn.setFixedSize(120, 35)
        image_btn.clicked.connect(self.show_image_manager)
        header.addWidget(image_btn)
        
      
        # 添加配置按钮
        add_btn = StyledButton("添加模拟器", "icons/add.png")
        add_btn.setFixedSize(120, 35)
        add_btn.clicked.connect(self.show_config_dialog)
        header.addWidget(add_btn)
        
        main_layout.addLayout(header)
        
        # 创建列表显示模拟器
        self.emulator_list = QListWidget()
        self.emulator_list.setMinimumHeight(300)
        self.emulator_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        main_layout.addWidget(self.emulator_list)
        
        # 创建按钮容器
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # 添加弹簧让按钮靠右
        button_layout.addStretch()
        
        # 添加刷新按钮
        refresh_btn = StyledButton("刷新列表", "icons/refresh.png")
        refresh_btn.clicked.connect(self.refresh_emulators)
        button_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(button_layout)
        
        # 添加 Toast 组件
        self.toast = Toast(self)
    
    def check_environment(self):
        """检查环境"""
        if not find_avdmanager():
            # 打开环境管理对话框
            # 延时执行
            QTimer.singleShot(100, self.show_environment_dialog)
    
    def show_environment_dialog(self):
        """显示环境管理对话框"""
        dialog = EnvironmentDialog(self)
        dialog.exec()
    
    def show_image_manager(self):
        """显示镜像管理对话框"""
        dialog = ImageManagerDialog(self)
        dialog.exec()
    
    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = EmulatorConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # 获取配置信息
                name = dialog.name_edit.text()
                device = dialog.device_combo.currentData()  # 设备ID
                system_image = dialog.image_combo.currentData()  # 系统镜像ID
                ram = dialog.ram_spin.value()
                
                if not name:
                    self.toast.showMessage("请输入模拟器名称")
                    return
                
                if not device:
                    self.toast.showMessage("请选择设备类型")
                    return
                
                if not system_image:
                    self.toast.showMessage("请先在镜像管理中下载系统镜像")
                    return
                
                avdmanager = find_avdmanager()
                if not avdmanager:
                    raise Exception("找不到 avdmanager 工具")
                
                # 创建模拟器基本命令
                create_cmd = [
                    avdmanager, 'create', 'avd',
                    '-n', name,  # 模拟器名称
                    '-k', system_image,  # 系统镜像
                    '-d', device,  # 设备类型
                    '-c', 'hw.ramSize=2048M'  # 创建 2GB 的 SD 卡
                ]

                # 输出创建命令
                print("Creating AVD with command:", ' '.join(create_cmd))
                
                # 执行创建命令
                process = subprocess.Popen(
                    create_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,  # 添加标准输入以处理交互
                    universal_newlines=True
                )
                
                # 某些版本的 avdmanager 会询问是否自定义硬件配置
                # 我们自动回答"no"以使用默认配置
                output, _ = process.communicate(input='no\n')
                
                if process.returncode != 0:
                    raise Exception(f"创建失败: {output}")
                
                # 配置模拟器
                config_path = os.path.expanduser(f'~/.android/avd/{name}.avd/config.ini')
                with open(config_path, 'a') as f:
                    # 设置内存大小
                    f.write(f'\nhw.ramSize={ram}')
                    # 添加其他有用的配置
                    f.write('\nhw.keyboard=yes')  # 启用物理键盘
                    f.write('\ndisk.dataPartition.size=2048M')  # 设置数据分区大小
                    f.write('\nhw.gpu.enabled=yes')  # 启用 GPU 加速
                    f.write('\nhw.gpu.mode=auto')
                    f.write('\nhw.audioInput=yes')  # 启用音频输入
                    f.write('\nhw.audioOutput=yes')  # 启用音频输出
                    f.write('\nhw.camera.back=webcam0')  # 配置后置摄像头
                    f.write('\nhw.camera.front=webcam0')  # 配置前置摄像头
                
                self.toast.showMessage(f"模拟器 {name} 创建成功")
                self.refresh_emulators()
                
                # 根据开关状态决定是否启动模拟器
                if dialog.start_switch.isChecked():
                    QTimer.singleShot(1000, lambda: self.start_emulator(name))
                
            except Exception as e:
                self.toast.showMessage(f"创建模拟器失败：{str(e)}")

    def start_emulator(self, emulator_name):
        """启动指定的模拟器"""
        try:
            subprocess.Popen([EMULATOR_PATH, '-avd', emulator_name])
            self.toast.showMessage(f"正在启动模拟器：{emulator_name}")
            QTimer.singleShot(2000, self.refresh_emulators)
        except Exception as e:
            self.toast.showMessage(f"启动模拟器失败：{str(e)}")
    
    def refresh_emulators(self):
        """刷新模拟器列表"""
        self.emulator_list.clear()
        
        # 显示加载动画
        self.loading.show()
        
        # 创建并启动加载线程
        self.load_thread = EmulatorListThread()
        self.load_thread.finished.connect(self.handle_emulators_loaded)
        self.load_thread.error.connect(self.handle_load_error)
        self.load_thread.start()
    
    def handle_emulators_loaded(self, emulators, running_emulators):
        """处理模拟器列表加载完成"""
        try:
            for emu in emulators:
                status = "（运行中）" if emu in running_emulators else "（未运行）"
                item = QListWidgetItem(self.emulator_list)
                item_widget = EmulatorListItem(emu, status, self)
                item.setSizeHint(item_widget.sizeHint())
                self.emulator_list.setItemWidget(item, item_widget)
            
            # 关闭加载动画
            self.loading.hide()
            
        except Exception as e:
            self.handle_load_error(str(e))
    
    def handle_load_error(self, error_msg):
        """处理加载错误"""
        # 关闭加载动画
        self.loading.hide()
        self.toast.showMessage(f"获取模拟器列表失败：{error_msg}")

    def stop_emulator(self, emulator_name):
        """关闭指定的模拟器"""
        try:
            ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = ps_result.stdout.strip().split('\n')
            
            target_pid = None
            for process in processes:
                if 'qemu-system-' in process:
                    # 使用完整的 -avd 参数匹配
                    avd_parts = process.split('-avd ')
                    if len(avd_parts) > 1:
                        # 获取模拟器名称（取到下一个参数之前的部分）
                        emu_part = avd_parts[1].split(' -')[0]  # 获取到下一个参数之前的部分
                        emu_name = emu_part.strip()  # 移除可能的空格
                        if emu_name == emulator_name:  # 精确匹配
                            target_pid = process.split()[1]
                            break
            
            if target_pid:
                subprocess.run(['kill', target_pid])
                self.toast.showMessage(f"正在关闭模拟器：{emulator_name}")
                QTimer.singleShot(5000, self.refresh_emulators)
            else:
                self.toast.showMessage(f"模拟器 {emulator_name} 未在运行")
                self.refresh_emulators()
            
        except Exception as e:
            self.toast.showMessage(f"关闭模拟器失败：{str(e)}")

    def delete_emulator(self, emulator_name):
        """删除指定的模拟器"""
        # 添加确认对话框
        confirm = QMessageBox(self)
        confirm.setWindowTitle("确认删除")
        confirm.setText(f"确定要删除模拟器 {emulator_name} 吗？")
        confirm.setInformativeText("此操作不可恢复。")
        confirm.setIcon(QMessageBox.Icon.Warning)
        confirm.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirm.setDefaultButton(QMessageBox.StandardButton.No)
        
        # 设置样式
        confirm.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QPushButton {
                padding: 8px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton[text="Yes"] {
                background-color: #ff6b6b;
                color: white;
                border: none;
            }
            QPushButton[text="Yes"]:hover {
                background-color: #ee5253;
            }
            QPushButton[text="No"] {
                background-color: #f5f6fa;
                color: #2c3e50;
                border: 2px solid #dcdde1;
            }
            QPushButton[text="No"]:hover {
                background-color: #dcdde1;
            }
        """)
        
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                avdmanager = find_avdmanager()
                if not avdmanager:
                    raise Exception("找不到 avdmanager 工具")
                
                # 删除模拟器
                delete_cmd = [avdmanager, 'delete', 'avd', '-n', emulator_name]
                result = subprocess.run(delete_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(result.stderr or result.stdout)
                
                self.toast.showMessage(f"模拟器 {emulator_name} 已删除")
                self.refresh_emulators()
                
            except Exception as e:
                self.toast.showMessage(f"删除模拟器失败：{str(e)}")
