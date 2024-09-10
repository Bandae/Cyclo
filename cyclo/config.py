'''
Config file for setting up the root directory of the application.
It MUST be placed in the root of the project repository.
'''

import os
import sys

def dependencies_path(relative_path):
    # Check if running as a bundled application
    if getattr(sys, 'frozen', False):
        # If bundled, the executable's directory is the base path
        base_path = os.path.dirname(sys.executable)
    else:
        # If running in a development environment, get 
        # path to root directory of repository
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    dependency_path = os.path.join(base_path, relative_path)
    return dependency_path

def resource_path(relative_path):
    return os.path.normpath(os.path.join(relative_path))

# Set application name and icon
APP_NAME = 'Przekładnia Cykloidalna'
APP_ICON = dependencies_path('resources//icons//mainwindow_icon.png')