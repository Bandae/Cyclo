from PySide2.QtWidgets import QToolButton, QMenu, QWidgetAction, QCheckBox, QWidget, QHBoxLayout, QLabel 
from PySide2.QtGui import QIcon, QMouseEvent
from PySide2.QtCore import Signal

class ClickableLabel(QLabel):
    """
    A QLabel subclass that emits a clicked signal when it is clicked.
    """
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        event.ignore()

class RichTextCheckbox(QWidget):
    '''
    Custom checkbox implementing default checkbox and
    a clickable label, that allows rich text formatting.
    It purpose is to display subscripts properly.
    '''
    stateChanged = Signal(int)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.checkBox = QCheckBox()
        self.label = QLabel(text)

        self.layout.addWidget(self.checkBox)
        self.layout.addWidget(self.label)
        self.layout.addStretch()
        self.layout.setContentsMargins(2, 1, 1, 1)

        self.checkBox.stateChanged.connect(self.stateChanged.emit)

    def isChecked(self):
        return self.checkBox.isChecked()

    def setChecked(self, checked):
        self.checkBox.setChecked(checked)

    def setEnabled(self, enable):
        self.checkBox.setEnabled(enable)
        self.label.setEnabled(enable)

    def mousePressEvent(self, event):
        self.checkBox.setChecked(not self.checkBox.isChecked())
        super().mousePressEvent(event)

class CheckboxDropdown(QToolButton):
    """
    A custom QToolButton that displays a dropdown menu with checkboxes.
    """
    stateChanged = Signal()
    def __init__(self):
        super().__init__()
        
        self._checkboxes = {}

        self.setStyleSheet("""
            QToolButton::menu-indicator {
                image: none
            }                        
            QToolButton {
                background-color: transparent;
                color: black;
                border: 1px solid transparent;
                border-radius: 5px;
            }
            QToolButton:hover {
                background-color: #66beb2;
                border: 1px solid #66beb2;
            }
            QToolButton:pressed {
                background-color: #51988e;
                border: 1px solid #51988e;
            }
        """)
                                           
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self._menu = QMenu(self)
        self._menu.setToolTipsVisible(True)
        self.setMenu(self._menu)

    def addItem(self, id, label, description='', callback=None):
        """
        Add a checkable action to the dropdown menu.
        """
        if id not in self._checkboxes:
            checkbox = RichTextCheckbox(label)
            checkbox.setToolTip(description)

            if callback is None:
                checkbox.stateChanged.connect(self._emitStateChangedSignal)
            else:
                checkbox.stateChanged.connect(callback)

            # Create a QWidgetAction and set the checkbox as its widget
            widget_action = QWidgetAction(self)
            widget_action.setDefaultWidget(checkbox)

            # Add the QWidgetAction to the menu
            self._menu.addAction(widget_action)
            self._checkboxes[id] = checkbox
    
    def enableItem(self, id, enable=True):
        '''
        Enables or disables checkbox of given id.
        If disables, unchecks it.

        Args:
            id (str): id of checkbox.
            enabled (bool): if enable checkbox.
        '''
        if id in self._checkboxes:
            self._checkboxes[id].setEnabled(enable)
        if enable is False:
            self._checkboxes[id].setChecked(enable)
            self._emitStateChangedSignal()

    def checkItem(self, id, check):
        if id in self._checkboxes:
            if check != self.isChecked(id):
                self._checkboxes[id].setChecked(check)

    def isChecked(self, id):
        '''
        Check if Checkbox is checked.

        Args:
            id: (str): id of checkbox.

        Returns:
            res (bool): If checkobox of given id is checked.
        '''
        if id in self._checkboxes:
            return self._checkboxes[id].isChecked()
        return False
    
    def setIcon(self, icon, tootltip):
        '''
        Set icon of every checkbox.
        '''
        super().setIcon(QIcon(icon))

        self.setToolTip(tootltip)

    def getItems(self):
        """
        Return all items ids. 
        Returns:
            res (list): List of tuples (id, text) for of every checked checkbox.
        """
        res = []
        for id in self._checkboxes.keys():
                res.append(id)
        return res

    def getCheckedItems(self):
        """
        Return checked items ids.

        Returns:
            res (list): List of tuples (id, text) for of every checked checkbox.
        """
        res = []
        for id, action in self._checkboxes.items():
            if action.isChecked():
                res.append(id)
        return res

    def _emitStateChangedSignal(self):
        self.stateChanged.emit()
