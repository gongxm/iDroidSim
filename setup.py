from setuptools import setup, find_packages

APP = ['main.py']
DATA_FILES = [
    ('icons', ['icons/app.icns', 'icons/loading.gif','icons/refresh.png', 'icons/start.png', 'icons/stop.png', 'icons/add.png', 'icons/down-arrow.png', 'icons/delete.png','icons/image.png', 'icons/settings.png'])
]
OPTIONS = {
    'iconfile': 'icons/app.icns',
    'packages': ['PyQt6', 'requests', 'charset_normalizer'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    'excludes': ['tkinter'],
    'plist': {
        'CFBundleName': "iDroidSim",
        'CFBundleDisplayName': "iDroidSim",
        'CFBundleIdentifier': "com.gongxm.iDroidSim",
        'CFBundleVersion': "1.0.0",
        'LSMinimumSystemVersion': '10.13',
    }
}

setup(
    name="iDroidSim",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'requests',
        'charset-normalizer>=2.0.0'
    ],
    entry_points={
        'console_scripts': [
            'iDroidSim=main:main',
        ],
    },
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 