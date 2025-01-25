from abc import ABC, ABCMeta, abstractmethod
from ast import literal_eval

from PySide2.QtCore import Signal, Qt, QSize
from PySide2.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QSizePolicy 
from PySide2.QtGui import QIcon, QFont

from .pyqt_helpers import createDataInputRow
from .ShaftSubsection import ShaftSubsection

from config import RESOURCES_DIR_NAME, dependencies_path

class CustomFrame(QFrame):
    def __init__(self):
        super().__init__()

        self._defaultStyle = "QFrame { background-color: #8ad6cc; border-radius: 5px;}"
        self._onHoverStyle = "QFrame { background-color: #66beb2; border-radius: 5px;}"
        self.setStyleSheet(self._defaultStyle)

class HoverButton(QPushButton):
    def __init__(self, parent: QFrame):
        super().__init__(parent)

        self.setStyleSheet("""                                                  
            QPushButton {
                background-color: transparent;
            }
            """)

    def enterEvent(self, event):
        self.parent().setStyleSheet(self.parent()._onHoverStyle)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.parent().setStyleSheet(self.parent()._defaultStyle)
        super().leaveEvent(event)

class HeaderButton(HoverButton):
    def __init__(self, parent: QFrame):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        parentStyle = self.styleSheet()
        newStyle = "QPushButton {text-align: left; padding-left: 10px}"
        self.setStyleSheet(parentStyle + newStyle)
        font = QFont("Arial", 10, QFont.Bold)
        self.setFont(font)

class ABCQWidgetMeta(ABCMeta, type(QWidget)):
    pass

class Section(QWidget, metaclass=ABCQWidgetMeta):
    subsectionDataSignal = Signal(tuple)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self._name = name
        self.subsections = []
        self.subsectionCount = 0

        self._initUI()

    def _initUI(self):
        self._mainLayout = QVBoxLayout(self)
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        
        self._initHeader()
        self._initContent()
    
    def _initHeader(self):
        # Set header layout
        header = CustomFrame()
        self._headerHeight = 25
        header.setFixedHeight(self._headerHeight)
        self._mainLayout.addWidget(header)

        self._headerLayout = QHBoxLayout()
        self._headerLayout.setContentsMargins(0, 0, 0, 0)
        self._headerLayout.setSpacing(0)
        self._headerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setLayout(self._headerLayout)

        # Set toggle section button
        self.toggleHeaderButton = HeaderButton(header)
        
        self.toggleHeaderButton.setText(self._name)
        self.toggleHeaderButton.clicked.connect(self.toggleContent)
        self._headerLayout.addWidget(self.toggleHeaderButton)
    
    def _initContent(self):
        # Set content layout
        self._content = QFrame()
        self._contentLayout = QVBoxLayout()
        self._contentLayout.setContentsMargins(5, 0, 0, 0)
        self._content.setLayout(self._contentLayout)

        self._mainLayout.addWidget(self._content)

        self._content.setVisible(False)

    def toggleContent(self, event):
        '''
        Toggle the visibility of the content section
        '''
        self._content.setVisible(not self._content.isVisible())

    @abstractmethod
    def handleSubsectionData(self, data):
        pass

class ShaftSection(Section):
    addSubsectionSignal = Signal()
    removeSubsectionPlotSignal = Signal(str, int)

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._subsectionName = 'Stopień'
    
    def _initHeader(self):
        super()._initHeader()
        # Set add subsection button
        self._addSubHeaderButton = QPushButton()
        buttonSize = self._headerHeight
        iconSize = self._headerHeight * 0.9
        self._addSubHeaderButton.setFixedSize(buttonSize, buttonSize)
        self._addSubHeaderButton.setIconSize(QSize(iconSize, iconSize))
        self._addSubHeaderButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//add_icon.png')))
        self._addSubHeaderButton.setToolTip('Dodaj')
        self._addSubHeaderButton.setStyleSheet("""                         
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
        
        self._addSubHeaderButton.clicked.connect(self.addSubsection)
        self._headerLayout.addWidget(self._addSubHeaderButton)

        self._addSubHeaderButton.setVisible(False)

    def addSubsection(self):
        subsection = ShaftSubsection(self._subsectionName, self.subsectionCount, self)
        subsection.setAttributes([('d', 'Ø'), ('l', 'l')])
        subsection.subsectionDataSignal.connect(self.handleSubsectionData)
        subsection.removeSubsectionSignal.connect(self.removeSubsection)
        self.subsections.append(subsection)
        self._contentLayout.addWidget(subsection)
        self.subsectionCount += 1
        self.setAddSubHeaderButtonEnabled(False)
        self.addSubsectionSignal.emit()

    def removeSubsection(self, subsectionNumber):
        # Find and remove the specific subsection
        subsectionToRemove = self.sender()
        self._contentLayout.removeWidget(subsectionToRemove)
        subsectionToRemove.deleteLater()
        self.subsections = [s for s in self.subsections if s != subsectionToRemove]
    
        # Update the numbers and names of the remaining subsections
        for i, subsection in enumerate(self.subsections):
            subsection.updateSubsectionName(i)

        # Update the subsection count
        self.subsectionCount -= 1
        
        self.removeSubsectionPlotSignal.emit(self._name, subsectionNumber)

    def setLimits(self, limits):
        for subsectionNumber, attributes in limits.items():
            self.subsections[subsectionNumber].setLimits(attributes)

    def setValues(self, values):
        for subsectionNumber, attributes in values.items():
                self.subsections[subsectionNumber].setValues(attributes)

    def setAddSubHeaderButtonEnabled(self, enabled):
        self._addSubHeaderButton.setEnabled(enabled)
    
    def toggleContent(self, event):
        super().toggleContent(event)
        self._addSubHeaderButton.setVisible(not self._addSubHeaderButton.isVisible())

    def handleSubsectionData(self, subsectionData):
        subsection = self.sender()
        commonSectionData = None
        data = (self._name, subsection.subsectionNumber, subsectionData, commonSectionData)
        self.subsectionDataSignal.emit(data)

class EccentricsSection(Section):
    removeSubsectionPlotSignal = Signal(str, int)

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.subsectionName = 'Mimośród'

    def _initContent(self):
        super()._initContent()

        # Set data entries
        self.inputs = {}
        
        attribute, symbol = ('d', 'Ø')
        attributeRow, input = createDataInputRow(symbol)
        self._contentLayout.addLayout(attributeRow)
        
        self.inputs[attribute] = input

    def setSubsectionsNumber(self, sectionsNumber):
        if self.subsectionCount < sectionsNumber:
            # Add subsections
            for _ in range(self.subsectionCount, sectionsNumber):
                subsection = ShaftSubsection(self.subsectionName, self.subsectionCount, self)
                subsection.setAttributes([('l', 'l')])
                for attribute, input in self.inputs.items():
                    subsection.addInput(attribute, input)
                subsection.removeButton.hide()
                subsection.subsectionDataSignal.connect(self.handleSubsectionData)
                self.subsections.append(subsection)
                self._contentLayout.addWidget(subsection)
                self.subsectionCount += 1
        elif self.subsectionCount > sectionsNumber:
            # Remove subsections
            while self.subsectionCount > sectionsNumber:
                lastSubsectionNumber = self.subsectionCount - 1
                self.removeSubsection(lastSubsectionNumber)

    def removeSubsection(self, subsectionNumber):
        # Find and remove the specific subsection
        subsectionToRemove = self.subsections[subsectionNumber]
        self._contentLayout.removeWidget(subsectionToRemove)
        subsectionToRemove.deleteLater()
        self.subsections = [s for s in self.subsections if s != subsectionToRemove]
    
        # Update the numbers and names of the remaining subsections
        for i, subsection in enumerate(self.subsections):
            subsection.updateSubsectionName(i)

        # Update the subsection count
        self.subsectionCount -= 1
        
        self.removeSubsectionPlotSignal.emit(self._name, subsectionNumber)

    def setLimits(self, limits):
        for subsectionNumber, attributes in limits.items():
            self.subsections[subsectionNumber].setLimits(attributes)
        
    def setValues(self, values):
        for subsectionNumber, attributes in values.items():
                self.subsections[subsectionNumber].setValues(attributes)

    def handleSubsectionData(self, subsectionData):
        subsection = self.sender()
        commonSectionData = {key: literal_eval(input.text()) for key, input in self.inputs.items()}
        data = (self._name, subsection.subsectionNumber, subsectionData, commonSectionData)
        self.subsectionDataSignal.emit(data)
