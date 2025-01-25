from typing import Callable
from PySide2.QtWidgets import QLayout, QVBoxLayout, QWidget

from .ITrackedWidget import ITrackedWidget

class Section(ITrackedWidget):
    """
    QWidget instance that derrives from ITrackedWidget abstract class.

    It implements a basic widget like class.
    """
    def __init__(self, parent: QWidget, name: str, callback: Callable):
        """
        parent (QWidget): Parent (UI) of this module.
        name (str): instance ID.
        callback (Callable): method to be called 
        """
        super().__init__(parent, callback)
        self.initUI()
        self._name = name

    def initUI(self):
        """
        Init the user interface.
        """
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

    def addWidget(self, widget: QWidget):
        """
        Add widget.

        Args:
            widget (QWidget): widget to add.
        """
        self.mainLayout.addWidget(widget)
        self._setupStateTracking()

    def addLayout(self, layout: QLayout):
        """
        Add layout.

        Args:
            layout (QWidget): layout to add.
        """
        self.mainLayout.addLayout(layout)
        self._setupStateTracking()

    def _onStateChecked(self, allProvided: bool, stateChanged: bool):
        """
        Override the parent class method called after state checking.

        Add name to the callback attributes.

        Args:
            allProvided (bool): Speciefies whether all inputs are provided.
            stateChanged (bool): Speciefies whether the inputs has been changed.
        """
        self._callback(self._name, allProvided, stateChanged)
