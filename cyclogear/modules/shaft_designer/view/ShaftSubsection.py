from ast import literal_eval

from PySide2.QtCore import Signal, Qt, QSize
from PySide2.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from PySide2.QtGui import QIcon

from config import RESOURCES_DIR_NAME, dependencies_path

from .pyqt_helpers import createDataInputRow, formatInput

class CustomFrame(QFrame):
    def __init__(self):
        super().__init__()
        self._defaultStyle = "QFrame { background-color: #8ad6cc; border-radius: 5px;}"
        self._onHoverStyle = "QFrame { background-color: #66beb2; border-radius: 5px;}"
        self.setStyleSheet(self._defaultStyle)

class HoverButton(QPushButton):
    def __init__(self, parent: QFrame):
        super().__init__(parent)

    def enterEvent(self, event):
        self.parent().setStyleSheet(self.parent()._onHoverStyle)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.parent().setStyleSheet(self.parent()._defaultStyle)
        super().leaveEvent(event)

class ShaftSubsection(QWidget):
    subsectionDataSignal = Signal(dict)
    removeSubsectionSignal = Signal(int)

    def __init__(self, subsectionName, subsectionNumber, parent=None):
        super().__init__(parent)
        self.subsectionName = subsectionName
        self.subsectionNumber = subsectionNumber
        self.expanded = False
        self.inputs = {}
        self.limits = {}

        self._initUI()

    def _initUI(self):
        # Main layout
        self._mainLayout = QVBoxLayout(self)
        self._mainLayout.setContentsMargins(0, 0, 0, 0)

        self._initHeader()
        self._initContent()

        # Set initial view
        self._content.setVisible(False)
        self._confirmButton.setEnabled(False)
        self._confirmButton.setVisible(False)

    def _initHeader(self):
        # Set header layout
        header = CustomFrame()
        self.headerHeight = 25
        header.setFixedHeight(self.headerHeight)  # Set the height to 30 pixels
        self._mainLayout.addWidget(header)

        self._headerLayout = QHBoxLayout()
        self._headerLayout.setContentsMargins(0, 0, 0, 0)
        self._headerLayout.setSpacing(0)
        self._headerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setLayout(self._headerLayout)

        # Set toggle section button
        self._toggleSectionButton = HoverButton(header)
        self._toggleSectionButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._toggleSectionButton.setStyleSheet("""                                                  
            QPushButton {
                background-color: transparent;
                text-align: left;
                font-size: 10pt;
                font-weight: 600;                                
                padding-left: 10px
            }
        """)

        self._setName()
        self._toggleSectionButton.clicked.connect(self.toggleContent)
        self._headerLayout.addWidget(self._toggleSectionButton)

        # Set confirmation button
        self._confirmButton = QPushButton()
        buttonSize = self.headerHeight
        iconSize = self.headerHeight * 0.9
        self._confirmButton.setFixedSize(buttonSize, buttonSize)
        self._confirmButton.setIconSize(QSize(iconSize, iconSize))
        self._confirmButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//confirm_icon.png')))
        self._confirmButton.setToolTip('Zatwierdź')
        self._confirmButton.setStyleSheet("""                         
            QPushButton {
                background-color: transparent;
                color: black;
                border: 1px solid transparent;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #66beb2;
                border: 1px solid #66beb2;
            }
            QPushButton:pressed {
                background-color: #51988e;
                border: 1px solid #51988e;
            }
        """)
        self._confirmButton.clicked.connect(self.emitDataSignal)
        self._headerLayout.addWidget(self._confirmButton)

        # Set removal button
        self.removeButton = QPushButton()
        buttonSize = self.headerHeight
        iconSize = self.headerHeight * 0.9
        self.removeButton.setFixedSize(buttonSize, buttonSize)
        self.removeButton.setIconSize(QSize(iconSize, iconSize))
        self.removeButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//remove_icon.png')))
        self.removeButton.setToolTip('Usuń')
        self.removeButton.setStyleSheet("""                         
            QPushButton {
                background-color: transparent;
                color: black;
                border: 1px solid transparent;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #66beb2;
                border: 1px solid #66beb2;
            }
            QPushButton:pressed {
                background-color: #51988e;
                border: 1px solid #51988e;
            }
        """)
        self.removeButton.clicked.connect(self.emitRemoveSignal)
        self._headerLayout.addWidget(self.removeButton)

    def _initContent(self):
        # _content layout
        self._content = QFrame()
        self._contentLayout = QVBoxLayout()
        self._content.setLayout(self._contentLayout)
        self._contentLayout.setContentsMargins(5, 0, 0, 0)
        self._mainLayout.addWidget(self._content)
        
        # Inputs layout
        self._inputsLayout = QVBoxLayout()
        self._contentLayout.addLayout(self._inputsLayout)
    
    def _setName(self):
        self._toggleSectionButton.setText(f'{self.subsectionName} {self.subsectionNumber + 1}')
    
    def _checkIfAllInputsProvided(self):
        self._confirmButton.setEnabled(all(input.text() != '' for input in self.inputs.values()) and all(literal_eval(input.text()) != 0 for input in self.inputs.values()))
    
    def _checkIfMeetsLimits(self):
        input = self.sender()
        attribute = next((key for key, value in self.inputs.items() if value == input), None)

        if attribute:
            min = self.limits[attribute]['min']
            max = self.limits[attribute]['max']
            value = float(input.text()) if input.text() else None

            if value is not None and value != 0:
                if min <= value <= max:
                    input.setText(f'{formatInput(value)}')
                elif min > value:
                    input.setText(f'{formatInput(min)}')
                elif max < value:
                    input.setText(f'{formatInput(max)}')
            else:
                input.clear()

    def setAttributes(self, attributes):
        # Set data entries
        for attribute in attributes:
            id = attribute[0]
            symbol = attribute[1]

            attributeRow, input = createDataInputRow(symbol)
            self._inputsLayout.addLayout(attributeRow)

            self.addInput(id, input)
    
    def addInput(self, id, input):
        input.textChanged.connect(self._checkIfAllInputsProvided)
        input.editingFinished.connect(self._checkIfMeetsLimits)
        self.inputs[id] = input

    def getAttributes(self):
        return {key: literal_eval(input.text()) for key, input in self.inputs.items()}
    
    def updateSubsectionName(self, newNumber):
        self.subsectionNumber = newNumber
        self._setName()
    
    def setLimits(self, limits):
        for attribute, attributeLimits in limits.items():
            if attribute in self.inputs.keys():
                self.limits[attribute] = {}
                min = attributeLimits['min']
                max = attributeLimits['max']
                self.limits[attribute]['min'] = min
                self.limits[attribute]['max'] = max
                self.inputs[attribute].setPlaceholderText(f'{formatInput(min)}-{formatInput(max)}')
    
    def setValues(self, values):
        for attribute, value in values.items():
            if attribute in self.inputs.keys():
                if value is not None and value != 0:
                    self.inputs[attribute].setText(f'{formatInput(value)}')
                else:
                     self.inputs[attribute].clear()

    def toggleContent(self, event):
        self._content.setVisible(not self._content.isVisible())
        self._confirmButton.setVisible(not self._confirmButton.isVisible())

        self.adjustSize()
        self.updateGeometry()

    def emitDataSignal(self):
        self.subsectionDataSignal.emit(self.getAttributes())
    
    def emitRemoveSignal(self):
        self.removeSubsectionSignal.emit(self.subsectionNumber)
