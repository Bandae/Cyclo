from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_window.view.main_window import MainWindow

from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Signal

class AbstractTab(QWidget):
    '''Abstrakcyjna klasa do dziedziczenia przez każdą z naszych zakładek.'''

    dataChanged = Signal(dict)
    # sygnal wysyłany, kiedy zmienią się dane potrzebne dla innych zakładek

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
