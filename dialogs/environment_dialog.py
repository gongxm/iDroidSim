from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QGroupBox, QProgressBar, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import subprocess
import requests
import zipfile
import tempfile
import shutil
from ui.toast import Toast
from utils import find_avdmanager, ANDROID_HOME
import platform

class EnvironmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("环境管理")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.check_environment()
    
    def setup_ui(self):
        """设置界面"""
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }
            QPushButton {
                padding: 8px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                background-color: #2ecc71;
                color: white;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QPushButton#download-btn {
                background-color: #3498db;
            }
            QPushButton#download-btn:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Command-line Tools 检查
        tools_group = QGroupBox("Command-line Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        self.tools_status = QLabel()
        tools_layout.addWidget(self.tools_status)
        
        self.tools_download_btn = QPushButton("下载 Command-line Tools")
        self.tools_download_btn.setObjectName("download-btn")
        self.tools_download_btn.clicked.connect(self.download_cmdline_tools)
        tools_layout.addWidget(self.tools_download_btn)
        self.tools_download_btn.hide()
        
        layout.addWidget(tools_group)
        
        # Platform Tools 组件检查
        platform_tools_group = QGroupBox("Platform Tools 组件")
        platform_tools_layout = QVBoxLayout(platform_tools_group)
        
        self.platform_tools_status = QLabel()
        platform_tools_layout.addWidget(self.platform_tools_status)
        
        self.platform_tools_download_btn = QPushButton("下载组件")
        self.platform_tools_download_btn.setObjectName("download-btn")
        self.platform_tools_download_btn.clicked.connect(self.download_platform_tools)
        platform_tools_layout.addWidget(self.platform_tools_download_btn)
        self.platform_tools_download_btn.hide()
        
        layout.addWidget(platform_tools_group)
        
        # Emulator 组件检查
        emulator_group = QGroupBox("Emulator 组件")
        emulator_layout = QVBoxLayout(emulator_group)
        
        self.emulator_status = QLabel()
        emulator_layout.addWidget(self.emulator_status)
        
        self.emulator_download_btn = QPushButton("下载组件")
        self.emulator_download_btn.setObjectName("download-btn")
        self.emulator_download_btn.clicked.connect(self.download_emulator)
        emulator_layout.addWidget(self.emulator_download_btn)
        self.emulator_download_btn.hide()
        
        layout.addWidget(emulator_group)
        
        # Platform 组件检查
        platform_group = QGroupBox("Android Platform 组件")
        platform_layout = QVBoxLayout(platform_group)
        
        self.platform_status = QLabel()
        platform_layout.addWidget(self.platform_status)
        
        self.platform_download_btn = QPushButton("下载组件")
        self.platform_download_btn.setObjectName("download-btn")
        self.platform_download_btn.clicked.connect(self.download_platform)
        platform_layout.addWidget(self.platform_download_btn)
        self.platform_download_btn.hide()
        
        layout.addWidget(platform_group)
        
        # 添加进度条
        self.progress_group = QGroupBox("下载进度")
        self.progress_group.hide()
        progress_layout = QVBoxLayout(self.progress_group)
        
        self.progress_label = QLabel("准备下载...")
        self.progress_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 14px;
            margin-bottom: 10px;
        """)
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
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
        """)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.progress_group)
        
        # 添加底部按钮布局
        bottom_layout = QHBoxLayout()
        
        # 添加一键检测按钮
        self.check_all_btn = QPushButton("一键检测")
        self.check_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.check_all_btn.clicked.connect(self.check_and_install_all)
        bottom_layout.addWidget(self.check_all_btn)
        
        bottom_layout.addStretch()
        
        # 添加关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f6fa;
                color: #2c3e50;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #dcdde1;
            }
            QPushButton[cancel="true"] {
                background-color: #ff6b6b;
                color: white;
                border: none;
            }
            QPushButton[cancel="true"]:hover {
                background-color: #ee5253;
            }
        """)
        self.close_btn.clicked.connect(self.handle_close)
        bottom_layout.addWidget(self.close_btn)
        
        layout.addLayout(bottom_layout)
        
        # 添加 Toast 组件
        self.toast = Toast(self)
        
        # 添加下载线程属性
        self.download_thread = None

    def check_environment(self):
        """检查环境配置"""
        # 检查 avdmanager
        avdmanager = find_avdmanager()
        if avdmanager:
            self.tools_status.setText("✅ Command-line Tools 已安装")
            self.tools_status.setStyleSheet("color: #2ecc71")
            self.tools_download_btn.hide()
        else:
            self.tools_status.setText("❌ 未找到 Command-line Tools")
            self.tools_status.setStyleSheet("color: #e74c3c")
            self.tools_download_btn.show()
        
        # 检查 platform-tools (adb)
        adb_path = os.path.join(ANDROID_HOME, 'platform-tools/adb')
        if os.path.exists(adb_path):
            self.platform_tools_status.setText("✅ Platform Tools 组件已安装")
            self.platform_tools_status.setStyleSheet("color: #2ecc71")
            self.platform_tools_download_btn.hide()
        else:
            self.platform_tools_status.setText("❌ Platform Tools 组件缺失")
            self.platform_tools_status.setStyleSheet("color: #e74c3c")
            self.platform_tools_download_btn.show()
        
        # 检查 emulator
        emulator_path = os.path.join(ANDROID_HOME, 'emulator/emulator')
        if os.path.exists(emulator_path):
            self.emulator_status.setText("✅ Emulator 组件已安装")
            self.emulator_status.setStyleSheet("color: #2ecc71")
            self.emulator_download_btn.hide()
        else:
            self.emulator_status.setText("❌ Emulator 组件缺失")
            self.emulator_status.setStyleSheet("color: #e74c3c")
            self.emulator_download_btn.show()
        
        # 检查 platform
        platforms_path = os.path.join(ANDROID_HOME, 'platforms')
        if os.path.exists(platforms_path) and os.listdir(platforms_path):  # 确保目录存在且不为空
            self.platform_status.setText("✅ Android Platform 组件已安装")
            self.platform_status.setStyleSheet("color: #2ecc71")
            self.platform_download_btn.hide()
        else:
            self.platform_status.setText("❌ Android Platform 组件缺失")
            self.platform_status.setStyleSheet("color: #e74c3c")
            self.platform_download_btn.show()

    def show_progress(self, show=True, text="准备下载...", progress=0):
        """显示或隐藏进度条"""
        if show:
            self.progress_group.show()
            self.progress_label.setText(text)
            self.progress_bar.setValue(progress)
        else:
            self.progress_group.hide()

    def enable_all_buttons(self):
        """启用所有按钮"""
        self.check_all_btn.setEnabled(True)
        self.close_btn.setEnabled(True)
        self.tools_download_btn.setEnabled(True)
        self.platform_tools_download_btn.setEnabled(True)
        self.emulator_download_btn.setEnabled(True)
        self.platform_download_btn.setEnabled(True)

    def handle_close(self):
        """处理关闭按钮点击"""
        if self.download_thread and self.download_thread.isRunning():
            confirm = QMessageBox(self)
            confirm.setWindowTitle("确认关闭")
            confirm.setText("关闭对话框将会取消下载，确定要关闭吗？")
            confirm.setIcon(QMessageBox.Icon.Question)
            confirm.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            confirm.setDefaultButton(QMessageBox.StandardButton.No)
            
            if confirm.exec() == QMessageBox.StandardButton.Yes:
                # 取消下载
                self.download_thread.cancel()
                # 关闭对话框
                self.accept()
        else:
            self.accept()

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        if self.download_thread and self.download_thread.isRunning():
            confirm = QMessageBox(self)
            confirm.setWindowTitle("确认关闭")
            confirm.setText("关闭对话框将会取消下载，确定要关闭吗？")
            confirm.setIcon(QMessageBox.Icon.Question)
            confirm.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            confirm.setDefaultButton(QMessageBox.StandardButton.No)
            
            if confirm.exec() == QMessageBox.StandardButton.Yes:
                # 取消下载
                self.download_thread.cancel()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


    # 获取 Command-line Tools 下载地址
    def get_cmdline_tools_url(self):
        """获取最新的 Command-line Tools 下载地址"""
        try:
            # 获取系统信息
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            # 构建请求 URL
            url = "https://dl.google.com/android/repository/repository2-1.xml"
            response = requests.get(url)
            
            if response.status_code != 200:
                raise Exception("无法获取 Command-line Tools 信息")
            
            # 解析 XML 找到最新版本
            from xml.etree import ElementTree
            root = ElementTree.fromstring(response.content)
            
            # 根据系统选择下载链接
            if system == "darwin":  # macOS
                if "arm" in machine:  # Apple Silicon
                    platform_name = "macosx"
                else:  # Intel
                    platform_name = "macosx"
            elif system == "windows":
                platform_name = "windows"
            else:  # Linux
                platform_name = "linux"
            
            # 在 XML 中查找对应的下载链接
            for pkg in root.findall(".//remotePackage[@path='cmdline-tools;latest']"):
                for archive in pkg.findall(f".//archive[host-os='{platform_name}']"):
                    url = archive.find('complete/url').text
                    checksum = archive.find('complete/checksum').text
                    size = archive.find('complete/size').text
                    return {
                        'url': f"https://dl.google.com/android/repository/{url}",
                        'checksum': checksum,
                        'size': int(size)
                    }
            
            raise Exception("未找到适合当前系统的下载链接")
            
        except Exception as e:
            raise Exception(f"获取下载地址失败：{str(e)}")

    def download_cmdline_tools(self):
        """下载 Command-line Tools"""
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "commandlinetools.zip")
            
            # 创建并显示进度对话框
            self.progress = QProgressDialog(self)
            self.progress.setWindowTitle("下载中")
            self.progress.setLabelText("正在下载 Command-line Tools...")
            self.progress.setRange(0, 100)
            self.progress.setMinimumWidth(400)  # 设置最小宽度
            self.progress.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress.setAutoClose(True)
            self.progress.canceled.connect(self.cancel_download)
            
            # 设置进度对话框样式
            self.progress.setStyleSheet("""
                QProgressDialog {
                    background-color: white;
                    border-radius: 10px;
                }
                QLabel {
                    font-size: 14px;
                    color: #2c3e50;
                    padding: 10px;
                    min-height: 40px;  /* 增加标签高度 */
                }
                QProgressBar {
                    border: 2px solid #dcdde1;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #f5f6fa;
                    min-height: 25px;  /* 增加进度条高度 */
                    margin: 10px 20px;  /* 增加边距 */
                }
                QProgressBar::chunk {
                    background-color: #2ecc71;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #f5f6fa;
                    color: #2c3e50;
                    border: 2px solid #dcdde1;
                    border-radius: 5px;
                    padding: 8px 20px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 100px;
                    margin: 10px;  /* 增加按钮边距 */
                }
                QPushButton:hover {
                    background-color: #dcdde1;
                }
            """)
            
            # 获取最新的下载链接
            url = self.get_cmdline_tools_url()['url']
            
            # 创建下载线程
            self.download_thread = DownloadThread(url, zip_path)
            self.download_thread.progress.connect(self.update_progress)
            self.download_thread.finished.connect(lambda path: self.handle_download_finished(path, temp_dir))
            self.download_thread.error.connect(self.handle_download_error)
            
            # 显示进度对话框并开始下载
            self.progress.show()
            self.download_thread.start()
            
        except Exception as e:
            QMessageBox.warning(self, "下载错误", f"启动下载失败：{str(e)}")

    def handle_download_finished(self, download_path, temp_dir):
        """处理下载完成"""
        try:
            # 恢复按钮状态
            self.toast.showMessage(f"Command-line Tools 下载完成")
            
            # 创建目标目录
            sdk_root = os.path.expanduser("~/Library/Android/sdk")
            cmdline_tools_root = os.path.join(sdk_root, "cmdline-tools")
            os.makedirs(cmdline_tools_root, exist_ok=True)
            
            # 解压文件到临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 移动文件到正确的位置
                cmdline_tools_latest = os.path.join(cmdline_tools_root, "latest")
                if os.path.exists(cmdline_tools_latest):
                    shutil.rmtree(cmdline_tools_latest)
                
                # 移动解压出来的 cmdline-tools 目录到 latest
                extracted_tools = os.path.join(temp_dir, "cmdline-tools")
                os.rename(extracted_tools, cmdline_tools_latest)
            
            # 设置执行权限
            bin_dir = os.path.join(cmdline_tools_latest, "bin")
            for file in os.listdir(bin_dir):
                file_path = os.path.join(bin_dir, file)
                if os.path.isfile(file_path):
                    os.chmod(file_path, 0o755)
            
            # 删除下载的压缩包
            os.remove(download_path)
            
            # 配置环境变量
            shell_type = os.path.basename(os.environ.get('SHELL', '/bin/bash'))
            shell_path = '/bin/zsh' if shell_type == 'zsh' else '/bin/bash'
            rc_file = os.path.expanduser('~/.zshrc' if shell_type == 'zsh' else '~/.bashrc')
            
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
                f'export ANDROID_AVD_HOME="$HOME/.android/avd"',
                f'export PATH="$PATH:{sdk_root}/cmdline-tools/latest/bin"',
                f'export PATH="$PATH:{sdk_root}/platform-tools"',
                f'export PATH="$PATH:{sdk_root}/emulator"'
            ]
            
            # 检查是否已存在
            if 'ANDROID_SDK_ROOT' not in content:
                # 添加环境变量
                with open(rc_file, 'a') as f:
                    f.write('\n'.join(env_vars))
                
                # 执行 source 命令刷新环境变量
                try:
                    subprocess.run(
                        [shell_path, '-c', f'source {rc_file}'],
                        check=True,
                        capture_output=True
                    )
                    self.toast.showMessage("环境变量已自动刷新")
                except Exception as e:
                    print(f"刷新环境变量时出错: {str(e)}")
            
            # 刷新界面状态
            self.check_environment()
            
            # 如果在一键检测模式下，继续安装下一个组件
            if hasattr(self, 'current_install_index') and hasattr(self, 'install_queue'):
                self.handle_component_finished()
            
        except Exception as e:
            QMessageBox.warning(self, "安装错误", f"安装工具失败：{str(e)}")

    def download_platform_tools(self):
        """下载 Platform Tools 组件"""
        try:
            # 检查是否有 sdkmanager
            avdmanager = find_avdmanager()
            if not avdmanager:
                QMessageBox.warning(self, "错误", "请先安装 Command-line Tools")
                return
            
            sdkmanager = os.path.join(os.path.dirname(avdmanager), 'sdkmanager')
            
            # 更改按钮状态
            self.platform_tools_download_btn.setText("下载中...")
            self.platform_tools_download_btn.setEnabled(False)
            
            # 显示进度组
            self.progress_group.show()
            self.progress_label.setText("正在下载 Platform Tools 组件...")
            # 设置进度条为循环模式
            self.progress_bar.setRange(0, 0)
            
            # 创建一个 QThread 来执行下载
            class PlatformToolsInstallThread(QThread):
                finished = pyqtSignal(bool, str)  # 成功/失败, 错误信息
                
                def run(self):
                    try:
                        process = subprocess.Popen(
                            [sdkmanager, "--install", "platform-tools"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        # 自动输入 'y' 确认安装
                        output, error = process.communicate(input='y\n')
                        
                        if process.returncode != 0:
                            self.finished.emit(False, error or output)
                        else:
                            self.finished.emit(True, "")
                    except Exception as e:
                        self.finished.emit(False, str(e))
            
            # 创建并启动线程
            self.install_thread = PlatformToolsInstallThread()
            self.install_thread.finished.connect(self.handle_platform_tools_install_finished)
            self.install_thread.start()
            
        except Exception as e:
            self.progress_group.hide()
            self.platform_tools_download_btn.setText("下载组件")
            self.platform_tools_download_btn.setEnabled(True)
            QMessageBox.warning(self, "下载错误", f"下载 Platform Tools 组件失败：{str(e)}")

    def handle_platform_tools_install_finished(self, success, error_msg):
        """处理 Platform Tools 安装完成"""
        # 恢复进度条正常状态
        self.progress_bar.setRange(0, 100)
        self.progress_group.hide()
        self.platform_tools_download_btn.setEnabled(True)
        
        if success:
            self.toast.showMessage("Platform Tools 组件安装成功")
            self.check_environment()  # 更新界面
            if hasattr(self, 'current_install_index') and hasattr(self, 'install_queue'):
                self.handle_component_finished()
        else:
            self.platform_tools_download_btn.setText("下载组件")
            QMessageBox.warning(self, "安装错误", f"安装 Platform Tools 组件失败：{error_msg}")

    def download_emulator(self):
        """下载 Emulator 组件"""
        try:
            # 检查是否有 sdkmanager
            avdmanager = find_avdmanager()
            if not avdmanager:
                QMessageBox.warning(self, "错误", "请先安装 Command-line Tools")
                return
            
            sdkmanager = os.path.join(os.path.dirname(avdmanager), 'sdkmanager')
            
            # 更改按钮状态
            self.emulator_download_btn.setText("下载中...")
            self.emulator_download_btn.setEnabled(False)
            
            # 显示进度组
            self.progress_group.show()
            self.progress_label.setText("正在下载 Emulator 组件...")
            # 设置进度条为循环模式
            self.progress_bar.setRange(0, 0)
            
            # 创建一个 QThread 来执行下载
            class EmulatorInstallThread(QThread):
                finished = pyqtSignal(bool, str)  # 成功/失败, 错误信息
                
                def run(self):
                    try:
                        process = subprocess.Popen(
                            [sdkmanager, "--install", "emulator"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        # 自动输入 'y' 确认安装
                        output, error = process.communicate(input='y\n')
                        
                        if process.returncode != 0:
                            self.finished.emit(False, error or output)
                        else:
                            self.finished.emit(True, "")
                    except Exception as e:
                        self.finished.emit(False, str(e))
            
            # 创建并启动线程
            self.install_thread = EmulatorInstallThread()
            self.install_thread.finished.connect(self.handle_emulator_install_finished)
            self.install_thread.start()
            
        except Exception as e:
            self.progress_group.hide()
            self.emulator_download_btn.setText("下载组件")
            self.emulator_download_btn.setEnabled(True)
            QMessageBox.warning(self, "下载错误", f"下载 Emulator 组件失败：{str(e)}")

    def handle_emulator_install_finished(self, success, error_msg):
        """处理 Emulator 安装完成"""
        # 恢复进度条正常状态
        self.progress_bar.setRange(0, 100)
        self.progress_group.hide()
        self.emulator_download_btn.setEnabled(True)
        
        if success:
            self.toast.showMessage("Emulator 组件安装成功")
            self.check_environment()  # 更新界面
            if hasattr(self, 'current_install_index') and hasattr(self, 'install_queue'):
                self.handle_component_finished()
        else:
            self.emulator_download_btn.setText("下载组件")
            QMessageBox.warning(self, "安装错误", f"安装 Emulator 组件失败：{error_msg}")

    def download_platform(self):
        """下载 Android Platform 组件"""
        try:
            # 检查是否有 sdkmanager
            avdmanager = find_avdmanager()
            if not avdmanager:
                QMessageBox.warning(self, "错误", "请先安装 Command-line Tools")
                return
            
            sdkmanager = os.path.join(os.path.dirname(avdmanager), 'sdkmanager')
            
            # 更改按钮状态
            self.platform_download_btn.setText("下载中...")
            self.platform_download_btn.setEnabled(False)
            
            # 显示进度组
            self.progress_group.show()
            self.progress_label.setText("正在获取最新版本信息...")
            self.progress_bar.setRange(0, 0)
            
            # 创建一个 QThread 来执行下载
            class PlatformInstallThread(QThread):
                finished = pyqtSignal(bool, str)  # 成功/失败, 错误信息
                
                def run(self):
                    try:
                        # 获取最新的平台版本
                        list_cmd = [sdkmanager, '--list']
                        result = subprocess.run(list_cmd, capture_output=True, text=True)
                        
                        # 解析输出找到最新的平台版本
                        latest_platform = None
                        for line in result.stdout.split('\n'):
                            if 'platforms;android-' in line:
                                try:
                                    # 提取版本号
                                    version_str = line.split('platforms;android-')[1].split()[0]
                                    version_num = int(version_str.split('-')[0])
                                    if latest_platform is None or version_num > latest_platform:
                                        latest_platform = version_num
                                except:
                                    continue
                        
                        if not latest_platform:
                            self.finished.emit(False, "无法获取最新平台版本")
                            return
                        
                        # 安装最新平台
                        process = subprocess.Popen(
                            [sdkmanager, "--install", f"platforms;android-{latest_platform}"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        # 自动输入 'y' 确认安装
                        output, error = process.communicate(input='y\n')
                        
                        if process.returncode != 0:
                            self.finished.emit(False, error or output)
                        else:
                            self.finished.emit(True, str(latest_platform))
                    except Exception as e:
                        self.finished.emit(False, str(e))
            
            # 创建并启动线程
            self.install_thread = PlatformInstallThread()
            self.install_thread.finished.connect(self.handle_platform_install_finished)
            self.install_thread.start()
            
        except Exception as e:
            self.progress_group.hide()
            self.platform_download_btn.setText("下载组件")
            self.platform_download_btn.setEnabled(True)
            QMessageBox.warning(self, "下载错误", f"下载 Android Platform 组件失败：{str(e)}")

    def handle_platform_install_finished(self, success, msg):
        """处理 Platform 安装完成"""
        # 恢复进度条正常状态
        self.progress_bar.setRange(0, 100)
        self.progress_group.hide()
        self.platform_download_btn.setEnabled(True)
        
        if success:
            self.toast.showMessage(f"Android {msg} Platform 安装成功")
            self.check_environment()  # 更新界面
            if hasattr(self, 'current_install_index') and hasattr(self, 'install_queue'):
                self.handle_component_finished()
        else:
            self.platform_download_btn.setText("下载组件")
            QMessageBox.warning(self, "安装错误", f"安装 Android Platform 组件失败：{msg}")

    def check_and_install_all(self):
        """一键检测并安装所有缺失组件"""
        try:
            # 禁用所有按钮
            self.check_all_btn.setEnabled(False)
            self.close_btn.setEnabled(False)
            self.tools_download_btn.setEnabled(False)
            self.platform_tools_download_btn.setEnabled(False)
            self.emulator_download_btn.setEnabled(False)
            self.platform_download_btn.setEnabled(False)
            
            # 创建安装队列
            self.install_queue = []
            
            # 检查各组件
            if not find_avdmanager():
                self.install_queue.append(('cmdline-tools', self.download_cmdline_tools))
            
            if not os.path.exists(os.path.join(ANDROID_HOME, 'platform-tools/adb')):
                self.install_queue.append(('platform-tools', self.download_platform_tools))
            
            if not os.path.exists(os.path.join(ANDROID_HOME, 'emulator/emulator')):
                self.install_queue.append(('emulator', self.download_emulator))
            
            platforms_path = os.path.join(ANDROID_HOME, 'platforms')
            if not os.path.exists(platforms_path) or not os.listdir(platforms_path):
                self.install_queue.append(('platform', self.download_platform))
            
            if not self.install_queue:
                self.toast.showMessage("所有组件已安装")
                self.enable_all_buttons()
                return
            
            # 显示进度组
            self.progress_group.show()
            self.progress_label.setText(f"正在安装 {self.install_queue[0][0]} 组件...")
            self.progress_bar.setRange(0, len(self.install_queue))
            self.progress_bar.setValue(0)
            
            # 开始安装第一个组件
            self.current_install_index = 0
            self.install_next_component()
            
        except Exception as e:
            self.enable_all_buttons()
            QMessageBox.warning(self, "错误", f"检测安装失败：{str(e)}")

    def check_all_components_installed(self):
        """检查所有组件是否都已安装"""
        # 检查 Command-line Tools
        if not find_avdmanager():
            return False
        
        # 检查 Platform Tools
        if not os.path.exists(os.path.join(ANDROID_HOME, 'platform-tools/adb')):
            return False
        
        # 检查 Emulator
        if not os.path.exists(os.path.join(ANDROID_HOME, 'emulator/emulator')):
            return False
        
        # 检查 Platform
        platforms_path = os.path.join(ANDROID_HOME, 'platforms')
        if not os.path.exists(platforms_path) or not os.listdir(platforms_path):
            return False
        
        return True

    def handle_component_finished(self):
        """处理组件安装完成"""
        # 检查是否所有组件都已安装
        if self.check_all_components_installed():
            # 所有组件安装完成
            self.progress_group.hide()
            self.toast.showMessage("所有组件安装完成")
            self.enable_all_buttons()
            self.check_environment()  # 刷新状态
            # 修改关闭按钮文字
            self.close_btn.setText("关闭")
            self.close_btn.setProperty("cancel", False)
            self.close_btn.style().unpolish(self.close_btn)
            self.close_btn.style().polish(self.close_btn)
        else:
            # 继续安装下一个组件
            self.current_install_index += 1
            self.install_next_component()

    def install_next_component(self):
        """安装下一个组件"""
        if self.current_install_index >= len(self.install_queue):
            # 所有组件安装完成
            self.progress_group.hide()
            self.toast.showMessage("所有组件安装完成")
            self.enable_all_buttons()
            self.check_environment()  # 刷新状态
            # 修改关闭按钮文字
            self.close_btn.setText("关闭")
            self.close_btn.setProperty("cancel", False)
            self.close_btn.style().unpolish(self.close_btn)
            self.close_btn.style().polish(self.close_btn)
            return
        
        # 获取当前要安装的组件
        component_name, install_func = self.install_queue[self.current_install_index]
        self.progress_label.setText(f"正在安装 {component_name} 组件...")
        self.progress_bar.setValue(self.current_install_index)
        
        # 调用安装函数
        install_func()

    def cancel_download(self):
        """取消下载"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.toast.showMessage("下载已取消")

    def update_progress(self, progress, text):
        """更新进度"""
        if self.progress:
            self.progress.setValue(progress)
            if text:
                self.progress.setLabelText(text)

    def handle_download_error(self, error_msg):
        """处理下载错误"""
        QMessageBox.warning(self, "下载错误", error_msg)
        self.progress.close()

class DownloadThread(QThread):
    """下载线程"""
    progress = pyqtSignal(int, str)  # 进度信号
    finished = pyqtSignal(str)  # 完成信号
    error = pyqtSignal(str)  # 错误信号
    
    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self._is_cancelled = False
    
    def cancel(self):
        """取消下载"""
        self._is_cancelled = True
    
    def run(self):
        try:
            # 发送请求并获取文件大小
            response = requests.get(self.url, stream=True)
            response.raise_for_status()  # 检查请求是否成功
            total_size = int(response.headers.get('content-length', 0))
            
            # 下载文件
            downloaded = 0
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._is_cancelled:
                        raise Exception("下载已取消")
                    if chunk:
                        f.write(chunk)
                        f.flush()  # 立即写入磁盘
                        os.fsync(f.fileno())  # 确保写入磁盘
                        downloaded += len(chunk)
                        if total_size:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress, f"正在下载 Command-line Tools... {progress}%")
            
            # 验证文件大小
            if os.path.getsize(self.save_path) != total_size:
                raise Exception("文件下载不完整")
            
            # 下载完成后发送信号
            self.finished.emit(self.save_path)
            
        except Exception as e:
            # 发生错误时删除已下载的文件
            if os.path.exists(self.save_path):
                try:
                    os.remove(self.save_path)
                except:
                    pass
            self.error.emit(str(e)) 