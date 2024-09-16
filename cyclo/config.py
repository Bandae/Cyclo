import os
import sys

# -----------------------------------BASE DIR PATH CONFIGURATION------------------------------------
def get_base_dir_path():
    """
    Get the base directory path from which the dependencies will be looked up to.
    Handles both development and bundled environments.
    """
    # Check if running as a bundled application
    if getattr(sys, 'frozen', False):
        # If bundled, the executable's directory is the base path
        return os.path.dirname(sys.executable)
    else:
        # If running in a development environment, get 
        # path to root directory of repository - one directory level up
        return os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_DIR_PATH = get_base_dir_path()

# ------------------------SET FUNCTION ACCESSING THE PROPPER DEPENDENCY PATH------------------------
def dependencies_path(relative_path):
    """
    Resolves a relative path to an absolute path within the base directory.
    """
    dependency_path = os.path.join(BASE_DIR_PATH, os.path.normpath(relative_path))
    return dependency_path

# --------------------------------------------CONSTANTS---------------------------------------------
RESOURCES_DIR_NAME = 'resources'

# Set path to resources directory
RESOURCES_PATH = dependencies_path(RESOURCES_DIR_NAME)

# Set application name and icon
APP_NAME = 'Przekładnia Cykloidalna'
APP_ICON = dependencies_path(f'{RESOURCES_DIR_NAME}//icons//mainwindow_icon.png')