import os
import subprocess

# 应用名称
APP_NAME = "iDroidSim"
# DMG 名称
DMG_NAME = "iDroidSim"

def build_dmg():
    # 确保 dist 目录存在
    if not os.path.exists('dist'):
        print("Error: dist directory not found!")
        return
    
    # 创建临时目录用于构建 DMG
    subprocess.run(['rm', '-rf', 'tmp_dmg'])
    subprocess.run(['mkdir', 'tmp_dmg'])
    
    # 复制 .app 到临时目录
    subprocess.run(['cp', '-r', f'dist/{APP_NAME}.app', 'tmp_dmg/'])
    
    # 创建 Applications 链接
    subprocess.run(['ln', '-s', '/Applications', 'tmp_dmg/Applications'])
    
    # 删除已存在的 DMG 文件
    subprocess.run(['rm', '-f', f'dist/{DMG_NAME}.dmg'])
    
    # 创建 DMG
    subprocess.run([
        'hdiutil', 'create',
        '-volname', DMG_NAME,
        '-srcfolder', 'tmp_dmg',
        '-ov',
        '-format', 'UDZO',
        f'dist/{DMG_NAME}.dmg'
    ])
    
    # 清理临时目录
    subprocess.run(['rm', '-rf', 'tmp_dmg'])
    
    print(f"DMG created: dist/{DMG_NAME}.dmg")

if __name__ == '__main__':
    build_dmg() 