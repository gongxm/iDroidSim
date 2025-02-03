from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                            QPushButton,QMessageBox, QHBoxLayout, QDialog, QProgressDialog,
                            QTabWidget, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor

import os
import subprocess
from ui.toast import Toast
from utils import find_avdmanager
from ui.loading_dialog import LoadingDialog

class LoadImagesThread(QThread):
    """加载镜像数据的线程"""
    finished = pyqtSignal(list, list)  # 发送 (可用镜像列表, 已安装镜像列表)
    error = pyqtSignal(str)  # 发送错误信息
    
    def __init__(self):
        super().__init__()
        self._is_running = True
    
    def run(self):
        try:
            # 创建一个定时器线程
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(self.handle_timeout)
            timer.start(30000)  # 30秒超时
            
            sdkmanager = os.path.join(os.path.dirname(find_avdmanager()), 'sdkmanager')
            if not os.path.exists(sdkmanager):
                raise Exception("找不到 sdkmanager 工具")
            
            # 获取所有可用镜像
            list_cmd = [sdkmanager, '--list']
            result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
            
            # 获取已安装镜像
            installed_cmd = [sdkmanager, '--list_installed']
            installed_result = subprocess.run(installed_cmd, capture_output=True, text=True, timeout=30)
            
            # 如果线程已被终止，直接返回
            if not self._is_running:
                return
            
            # 解析可用镜像
            available_images = {}
            for line in result.stdout.split('\n'):
                if 'system-images;android-' in line:
                    try:
                        parts = line.strip().split('|')[0].strip().split(';')
                        version = parts[1].replace('android-', '')
                        image_type = parts[2]
                        arch = parts[3]
                        
                        image_id = f"{version};{image_type};{arch}"
                        is_installed = f'system-images;android-{version};{image_type};{arch}' in installed_result.stdout
                        
                        if image_id not in available_images:
                            available_images[image_id] = {
                                'version': version,
                                'type': image_type,
                                'arch': arch,
                                'installed': is_installed
                            }
                    except:
                        continue
            
            # 解析已安装镜像
            installed_images = []
            for line in installed_result.stdout.split('\n'):
                if 'system-images;android-' in line:
                    try:
                        parts = line.strip().split('|')[0].strip().split(';')
                        version = parts[1].replace('android-', '')
                        image_type = parts[2]
                        arch = parts[3]
                        
                        installed_images.append({
                            'version': version,
                            'type': image_type,
                            'arch': arch
                        })
                    except:
                        continue
            
            # 停止定时器
            timer.stop()
            
            # 如果线程仍在运行，发送结果
            if self._is_running:
                self.finished.emit(list(available_images.values()), installed_images)
            
        except subprocess.TimeoutExpired:
            self.error.emit("加载超时，请检查网络连接")
        except Exception as e:
            if self._is_running:
                self.error.emit(str(e))
    
    def handle_timeout(self):
        """处理超时"""
        self._is_running = False
        self.error.emit("加载超时，请检查网络连接")
    
    def stop(self):
        """停止线程"""
        self._is_running = False

class ImageManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Android 系统镜像管理")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 5px;
                border: none;
                background-color: #f5f6fa;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2ecc71;
                color: white;
            }
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                gridline-color: #f5f6fa;
            }
            QTableWidget::item {
                padding: 0 5px;
                min-height: 40px;
            }
            QTableWidget QTableWidgetItem {
                padding: 8px;
            }
            QPushButton[text="删除"] {
                background-color: #ff6b6b;
                min-width: 60px;
                max-width: 80px;
                min-height: 20px;
                margin: 5px;
                padding: 5px 10px;
            }
            QPushButton[text="删除"]:hover {
                background-color: #ee5253;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 可用镜像标签页
        available_tab = QWidget()
        available_layout = QVBoxLayout(available_tab)
        
        self.available_table = QTableWidget()
        self.available_table.setColumnCount(4)
        self.available_table.setHorizontalHeaderLabels(["版本", "类型", "架构", "状态"])
        self.available_table.horizontalHeader().setStretchLastSection(False)  # 取消最后一列自动拉伸
        self.available_table.setColumnWidth(0, 100)  # 版本列
        self.available_table.setColumnWidth(1, 350)  # 类型列加宽
        self.available_table.setColumnWidth(2, 150)  # 架构列
        self.available_table.setColumnWidth(3, 100)  # 状态列
        self.available_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        available_layout.addWidget(self.available_table)
        
        # 下载按钮容器
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 添加弹簧让按钮靠右
        
        # 下载按钮
        download_btn = QPushButton("下载选中的镜像")
        download_btn.setFixedHeight(35)  # 设置固定高度
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        download_btn.clicked.connect(self.download_selected)
        button_layout.addWidget(download_btn)
        
        available_layout.addLayout(button_layout)
        
        # 已安装镜像标签页
        installed_tab = QWidget()
        installed_layout = QVBoxLayout(installed_tab)
        
        self.installed_table = QTableWidget()
        self.installed_table.setColumnCount(4)
        self.installed_table.setHorizontalHeaderLabels(["版本", "类型", "架构", "操作"])
        self.installed_table.horizontalHeader().setStretchLastSection(False)
        self.installed_table.setColumnWidth(0, 100)  # 版本列
        self.installed_table.setColumnWidth(1, 350)  # 类型列加宽
        self.installed_table.setColumnWidth(2, 150)  # 架构列
        self.installed_table.setColumnWidth(3, 100)  # 操作列
        self.installed_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        installed_layout.addWidget(self.installed_table)
        
        # 添加标签页
        tab_widget.addTab(available_tab, "可用镜像")
        tab_widget.addTab(installed_tab, "已下载镜像")
        layout.addWidget(tab_widget)
        
        # 添加加载动画对话框
        self.loading = LoadingDialog(self)
        
        # 在对话框显示后加载数据
        QTimer.singleShot(100, self.init_data)
        
        # 添加 Toast 组件
        self.toast = Toast(self)
        
        # 在创建表格后设置行高
        self.available_table.verticalHeader().setDefaultSectionSize(50)  # 设置行高
        self.installed_table.verticalHeader().setDefaultSectionSize(50)  # 设置行高
        
        # 添加加载线程属性
        self.load_thread = None
    
    def init_data(self):
        """初始化数据"""
        
        # 加载数据
        self.load_images()
        
    
    def showEvent(self, event):
        """对话框显示事件"""
        super().showEvent(event)
    
    def get_version_sort_key(self, version_str):
        """获取版本号的排序键值"""
        try:
            # 处理带有后缀的版本号，如 '34-ext8'
            version = version_str.split('-')[0]  # 取主版本号
            return int(version)
        except:
            return 0  # 如果无法解析，返回0作为最低优先级

    def load_images(self):
        """加载镜像数据"""
        # 显示加载动画
        self.loading.show()
        
        # 创建并启动加载线程
        if self.load_thread:
            self.load_thread.stop()
        self.load_thread = LoadImagesThread()
        self.load_thread.finished.connect(self.handle_images_loaded)
        self.load_thread.error.connect(self.handle_load_error)
        self.load_thread.start()
    
    def handle_images_loaded(self, available_images, installed_images):
        """处理镜像数据加载完成"""
        try:
            # 按版本号和安装状态排序可用镜像
            available_images.sort(key=lambda x: (-int(x['installed']), -self.get_version_sort_key(x['version'])))
            
            # 更新可用镜像表格
            self.available_table.setRowCount(0)
            for image in available_images:
                row = self.available_table.rowCount()
                self.available_table.insertRow(row)
                self.available_table.setItem(row, 0, QTableWidgetItem(image['version']))
                self.available_table.setItem(row, 1, QTableWidgetItem(image['type']))
                self.available_table.setItem(row, 2, QTableWidgetItem(image['arch']))
                status_item = QTableWidgetItem("已下载" if image['installed'] else "未下载")
                status_item.setForeground(QColor("#2ecc71" if image['installed'] else "#95a5a6"))
                self.available_table.setItem(row, 3, status_item)
            
            # 按版本号排序已安装镜像
            installed_images.sort(key=lambda x: -self.get_version_sort_key(x['version']))
            
            # 更新已安装镜像表格
            self.installed_table.setRowCount(0)
            for image in installed_images:
                row = self.installed_table.rowCount()
                self.installed_table.insertRow(row)
                self.installed_table.setItem(row, 0, QTableWidgetItem(image['version']))
                self.installed_table.setItem(row, 1, QTableWidgetItem(image['type']))
                self.installed_table.setItem(row, 2, QTableWidgetItem(image['arch']))
                
                # 创建删除按钮容器
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                delete_btn = QPushButton("删除")
                delete_btn.setProperty("version", image['version'])
                delete_btn.setProperty("type", image['type'])
                delete_btn.setProperty("arch", image['arch'])
                delete_btn.clicked.connect(self.delete_image)
                
                layout.addWidget(delete_btn)
                self.installed_table.setCellWidget(row, 3, container)
            
            # 关闭加载动画
            self.loading.hide()
            
        except Exception as e:
            self.handle_load_error(str(e))
    
    def handle_load_error(self, error_msg):
        """处理加载错误"""
        # 关闭加载动画
        self.loading.hide()
        QMessageBox.warning(self, "错误", f"加载镜像列表失败：{error_msg}")
    
    def download_selected(self):
        """下载选中的镜像"""
        # 获取选中的行
        selected_rows = set(item.row() for item in self.available_table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要下载的镜像")
            return
        
        try:
            # 创建进度对话框
            self.progress = QProgressDialog("正在下载系统镜像...", "取消", 0, 0, self)
            self.progress.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress.setAutoClose(True)
            self.progress.setStyleSheet("""
                QProgressDialog {
                    background-color: white;
                    border-radius: 10px;
                }
                QLabel {
                    font-size: 14px;
                    color: #2c3e50;
                    padding: 10px;
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
            """)
            self.progress.show()
            
            # 获取 sdkmanager 路径
            sdkmanager = os.path.join(os.path.dirname(find_avdmanager()), 'sdkmanager')
            
            # 下载每个选中的镜像
            for row in selected_rows:
                version = self.available_table.item(row, 0).text()
                image_type = self.available_table.item(row, 1).text()
                arch = self.available_table.item(row, 2).text()
                
                system_image = f'system-images;android-{version};{image_type};{arch}'
                self.progress.setLabelText(f"正在下载 Android {version} 系统镜像...")
                
                # 创建并启动下载线程
                self.download_thread = ImageDownloadThread(sdkmanager, system_image)
                self.download_thread.progress.connect(self.handle_download_progress)
                self.download_thread.finished.connect(lambda v=version: self.handle_download_finished(v))
                self.download_thread.start()
                
                # 等待下载完成
                while self.download_thread.isRunning():
                    QApplication.processEvents()
                    if self.progress.wasCanceled():
                        break
            
            self.progress.close()
            
            # 刷新列表
            self.load_images()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"下载镜像失败：{str(e)}")
    
    def handle_download_progress(self, text, error):
        """处理下载进度"""
        if error:
            QMessageBox.warning(self, "错误", error)
            self.progress.close()
        elif text:
            self.progress.setLabelText(text)
    
    def handle_download_finished(self, version):
        """处理下载完成"""
        try:
            # 配置环境变量
            sdk_root = os.path.expanduser("~/Library/Android/sdk")
            shell_type = os.path.basename(os.environ.get('SHELL', '/bin/bash'))
            
            if shell_type == 'zsh':
                rc_file = os.path.expanduser('~/.zshrc')
            else:
                rc_file = os.path.expanduser('~/.bashrc')
            
            # 读取现有内容
            try:
                with open(rc_file, 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                content = ''
            
            # 准备要添加的环境变量
            env_vars = [
                f'\n# Android SDK',
                f'export ANDROID_SDK_ROOT="{sdk_root}"',
                f'export ANDROID_HOME="{sdk_root}"',
                f'export ANDROID_AVD_HOME="$HOME/.android/avd"',  # 添加 AVD 路径
                f'export PATH="$PATH:{sdk_root}/cmdline-tools/latest/bin"',
                f'export PATH="$PATH:{sdk_root}/platform-tools"',
                f'export PATH="$PATH:{sdk_root}/emulator"'  # 添加模拟器路径
            ]
            
            # 检查是否已存在
            if 'ANDROID_SDK_ROOT' not in content:
                # 添加环境变量
                with open(rc_file, 'a') as f:
                    f.write('\n'.join(env_vars))
                
                # 获取当前shell类型和路径
                shell_type = os.path.basename(os.environ.get('SHELL', '/bin/bash'))
                shell_path = '/bin/zsh' if shell_type == 'zsh' else '/bin/bash'
                
                try:
                    # 执行 source 命令刷新环境变量
                    subprocess.run(
                        [shell_path, '-c', f'source {rc_file}'],
                        check=True,
                        capture_output=True
                    )
                except Exception as e:
                    print(f"刷新环境变量时出错: {str(e)}")
                
                # 显示提示
                QMessageBox.information(
                    self,
                    "环境配置",
                    f"已将 Android SDK 环境变量添加到 {rc_file}\n"
                    "环境变量已自动刷新，如果遇到问题请重启终端。",
                    QMessageBox.StandardButton.Ok
                )
            
        except Exception as e:
            QMessageBox.warning(self, "安装错误", f"安装 Command-line Tools 失败：{str(e)}")

    def delete_image(self):
        """删除镜像"""
        sender = self.sender()
        version = sender.property("version")
        image_type = sender.property("type")
        arch = sender.property("arch")
        
        # 添加确认对话框
        confirm = QMessageBox(self)
        confirm.setWindowTitle("确认删除")
        confirm.setText(f"确定要删除 Android {version} ({image_type}) 系统镜像吗？")
        confirm.setInformativeText("删除后如果需要使用，需要重新下载。")
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
                # 创建并显示进度对话框
                progress = QProgressDialog(self)
                progress.setWindowTitle("删除中")
                progress.setLabelText(f"正在删除 Android {version} 系统镜像...")
                progress.setRange(0, 0)  # 设置为循环动画
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setAutoClose(True)
                progress.setCancelButton(None)  # 不显示取消按钮
                progress.setStyleSheet("""
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
                """)
                progress.show()
                
                system_image = f'system-images;android-{version};{image_type};{arch}'
                sdkmanager = os.path.join(os.path.dirname(find_avdmanager()), 'sdkmanager')
                
                # 修改删除命令的格式
                delete_cmd = [sdkmanager, '--uninstall', system_image]
                
                # 执行删除命令
                process = subprocess.Popen(
                    delete_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                
                # 等待命令完成
                output, _ = process.communicate()
                
                # 关闭进度对话框
                progress.close()
                
                if process.returncode != 0:
                    raise Exception(f"删除失败: {output}")
                
                # 刷新列表
                self.load_images()
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除镜像失败：{str(e)}")

    def closeEvent(self, event):
        """关闭事件"""
        # 停止加载线程
        if self.load_thread:
            self.load_thread.stop()
        super().closeEvent(event)

class ImageDownloadThread(QThread):
    """镜像下载线程"""
    progress = pyqtSignal(str, str)  # 进度信号 (文本, 错误信息)
    finished = pyqtSignal()  # 完成信号
    
    def __init__(self, sdkmanager, system_image):
        super().__init__()
        self.sdkmanager = sdkmanager
        self.system_image = system_image
        self._is_cancelled = False
    
    def run(self):
        try:
            # 使用 Popen 执行下载命令，并自动确认
            process = subprocess.Popen(
                [self.sdkmanager, '--install', self.system_image, '--verbose'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 自动输入 'y' 确认安装
            process.stdin.write('y\n')
            process.stdin.flush()
            
            # 读取输出并更新进度
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if "Downloading" in line:
                    try:
                        # 尝试从输出中提取进度
                        percent = line.split("%")[0].split()[-1]
                        self.progress.emit(f"正在下载... {percent}%", "")
                    except:
                        pass
                elif "Installing" in line:
                    self.progress.emit("正在安装...", "")
            
            if process.returncode != 0:
                error = process.stderr.read()
                self.progress.emit("", f"下载失败: {error}")
                return
            
            self.finished.emit()
            
        except Exception as e:
            self.progress.emit("", str(e))

