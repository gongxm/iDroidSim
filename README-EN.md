# iDroidSim
Android emulator for Mac

<img width="800" alt="image" src="https://github.com/user-attachments/assets/c38b691a-3546-4678-a89a-a6c96dd1c74b" />


# Introduction
iDroidSim is an Android emulator management tool for macOS, providing a graphical interface to manage Android Virtual Devices (AVD).

## Features

- Graphical interface for Android emulator management
- One-click create, start, stop and delete emulators
- Support for multiple device models (Pixel series, Nexus series, etc.)
- Online system image download and management
- Automatic Android SDK environment configuration
- Support for custom emulator configuration (memory size, etc.)

## System Requirements

- macOS 10.13 or higher
- Python 3.7+
- Disk space: At least 10GB recommended (for Android SDK and system images)

## Installation

1. Download the latest DMG installation package
2. Open the DMG file and drag iDroidSim to the Applications folder
3. If you receive a security warning on first launch, please allow the app to run in System Preferences

## Usage

1. On first launch, the software will automatically check and configure the Android SDK environment
2. Click "Image Manager" to download the required Android system images
3. Click "Add Emulator" to create a new virtual device
4. Manage all created emulators in the main interface

## Build & Package

```bash
# 1. Clean previous builds
rm -rf build dist

# 2. Build application
python setup.py py2app

# 3. Create DMG
python build_dmg.py
```

## Tech Stack

- Python 3
- PyQt6 - GUI framework
- py2app - macOS application packaging
- Android SDK Tools

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contributing Guidelines

Pull Requests and Issues are welcome. Before submitting code, please ensure:

1. Code follows the project's coding standards
2. Add necessary test cases
3. Update relevant documentation
4. Clear and concise commit messages

## Contact

For questions or suggestions, please contact through:

- Submit an Issue
- Email: gongxm2018@gmail.com 
