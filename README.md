# iDroidSim
Android emulator for Mac

# 简介
iDroidSim 是一个用于 macOS 的 Android 模拟器管理工具，提供了图形化界面来管理 Android 虚拟设备(AVD)。

## 功能特点

- 图形化界面管理 Android 模拟器
- 一键创建、启动、停止和删除模拟器
- 支持多种设备型号(Pixel系列、Nexus系列等)
- 系统镜像在线下载和管理
- 自动配置 Android SDK 环境
- 支持自定义模拟器配置(内存大小等)

## 系统要求

- macOS 10.13 或更高版本
- Python 3.7+
- 磁盘空间: 建议至少 10GB 可用空间(用于 Android SDK 和系统镜像)

## 安装说明

1. 下载最新版本的 DMG 安装包
2. 打开 DMG 文件，将 iDroidSim 拖入 Applications 文件夹
3. 首次运行时，如果提示安全性问题，请在系统偏好设置中允许运行

## 使用方法

1. 首次运行时，软件会自动检查并配置 Android SDK 环境
2. 点击"镜像管理"下载需要的 Android 系统镜像
3. 点击"添加模拟器"创建新的虚拟设备
4. 在主界面可以管理所有已创建的模拟器

## 打包发布

```bash
# 1. 清理之前的构建
rm -rf build dist

# 2. 构建应用
python setup.py py2app

# 3. 创建 DMG
python build_dmg.py
```

## 技术栈

- Python 3
- PyQt6 - GUI框架
- py2app - macOS应用打包
- Android SDK Tools

## 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交 Pull Request 或 Issue。在提交代码前，请确保：

1. 代码符合项目的编码规范
2. 添加必要的测试用例
3. 更新相关文档
4. 提交信息清晰明了

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至: gongxm2018@gmail.com

