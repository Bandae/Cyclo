import sys
import os

def is_frozen():
    """Check if the application is compiled with PyInstaller."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_base_dir():
    """Determine the base directory of the application."""
    if is_frozen():
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return sys._MEIPASS
    else:
        # Use the current directory where main.py is located
        return os.path.dirname(os.path.abspath(__file__))

base_dir = get_base_dir()

config_dir = base_dir

if config_dir not in sys.path:
    sys.path.append(config_dir)
