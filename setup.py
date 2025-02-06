from setuptools import setup

APP = ['main.py']
DATA_FILES = ['employee.json']  # Add any other files you want to include (e.g., icons)
OPTIONS = {
    'argv_emulation': True,
    'packages': ['customtkinter', 'tkinter'],  # Add any other required packages
    'plist': {
        'CFBundleName': 'EmployeeScheduler',
        'CFBundleShortVersionString': '1.0',
        'CFBundleIdentifier': 'com.yourcompany.EmployeeScheduler',
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
