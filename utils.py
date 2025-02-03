import os
import subprocess

# 在文件开头更新 ANDROID_HOME 的设置
def find_android_home():
    """查找 Android SDK 的路径"""
    # 首先检查环境变量
    android_home = os.getenv('ANDROID_HOME')
    if android_home and os.path.exists(android_home):
        return android_home
        
    # 检查常见的安装路径
    possible_homes = [
        os.path.expanduser('~/Library/Android/sdk'),
        os.path.expanduser('~/Android/Sdk'),
    ]
    
    for home in possible_homes:
        if os.path.exists(home):
            return home
            
    return None

def find_avdmanager():
    """查找 avdmanager 工具的路径"""
    # 首先检查环境变量
    android_home = os.getenv('ANDROID_HOME')
    if not android_home:
        # 检查常见的安装路径
        possible_homes = [
            os.path.expanduser('~/Library/Android/sdk'),
            os.path.expanduser('~/Android/Sdk'),
        ]
        for home in possible_homes:
            if os.path.exists(home):
                android_home = home
                break
    
    if not android_home:
        return None
        
    # 在 cmdline-tools 目录下查找所有可能的版本目录
    cmdline_tools = os.path.join(android_home, 'cmdline-tools')
    if os.path.exists(cmdline_tools):
        try:
            # 列出所有子目录
            all_dirs = [d for d in os.listdir(cmdline_tools) 
                       if os.path.isdir(os.path.join(cmdline_tools, d))]
            
            for dir_name in all_dirs:
                # 检查每个目录下的 bin/avdmanager
                path = os.path.join(cmdline_tools, dir_name, 'bin/avdmanager')
                if os.path.exists(path):
                    return path
                
                # 有些版本可能在 tools/bin 下
                path = os.path.join(cmdline_tools, dir_name, 'tools/bin/avdmanager')
                if os.path.exists(path):
                    return path
        except Exception as e:
            print(f"搜索 avdmanager 时出错: {str(e)}")
    
    # 检查旧版本的位置
    old_paths = [
        os.path.join(android_home, 'tools/bin/avdmanager'),
        os.path.join(android_home, 'tools/avdmanager'),
    ]
    for path in old_paths:
        if os.path.exists(path):
            return path
    
    # 如果还是找不到，尝试从 PATH 环境变量中查找
    try:
        which_result = subprocess.run(['which', 'avdmanager'], 
                                    capture_output=True, text=True)
        if which_result.returncode == 0:
            return which_result.stdout.strip()
    except:
        pass
    
    return None

# 全局常量
ANDROID_HOME = find_android_home() or os.path.expanduser('~/Library/Android/sdk')
EMULATOR_PATH = os.path.join(ANDROID_HOME, 'emulator/emulator')
ADB_PATH = os.path.join(ANDROID_HOME, 'platform-tools/adb') 