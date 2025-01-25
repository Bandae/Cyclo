from PySide2.QtCore import Signal, Qt
from PySide2.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget

from ...common.widgets.DataButton import DataButton
from ...common.widgets.Section import Section
from ...common.widgets.ITrackedTab import ITrackedTab
from ...common.pyqt_helpers import createDataDisplayRow, createDataInputRow, createHeader

class PowerLossTab(ITrackedTab):
    rollingElementDiameterProvided = Signal(str, bool, bool)
    sectionDataProvided = Signal(str, bool, bool)

    def _initSelector(self):
        selectorLayout = QHBoxLayout()

        layoutSelectorLabel = createHeader('Miejsce osadzenia łożyska:', bold=True)

        self.layoutSelector = QComboBox()
        self.layoutSelector.setFixedWidth(150)
        self.layoutSelector.setEditable(True)
        lineEdit = self.layoutSelector.lineEdit()
        lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lineEdit.setReadOnly(True)
        
        self.layoutSelector.addItems(["Podpora przesuwna A", "Podpora stała B", "Mimośrody"])
        self.layoutSelector.currentIndexChanged.connect(self._onChangeSection)

        selectorLayout.addWidget(layoutSelectorLabel, alignment=Qt.AlignmentFlag.AlignLeft)
        selectorLayout.addWidget(self.layoutSelector, alignment=Qt.AlignmentFlag.AlignLeft)
        selectorLayout.addStretch(1)

        self.mainLayout.addLayout(selectorLayout)

    def _initSections(self):
        self.stackedSections = QStackedWidget()

        for sectionName in self._items['Bearings']:
            container = self._initBearingsSection(sectionName)
            self.stackedSections.addWidget(container)

        self.mainLayout.addWidget(self.stackedSections)

    def _initBearingsSection(self, sectionName):
        """
        Create and layout the UI components for single bearing section.
        """
        sectionLayout = QVBoxLayout()

        # Set content container
        container = QWidget()
        container.setLayout(sectionLayout)

        # Set button for bearing selection
        buttonLayout = QHBoxLayout()
        buttonLabel = createHeader('Znormalizowana średnica elementu tocznego:', bold=True)

        selectRollingElementButton = DataButton('Wybierz element toczny')
        self._items['Bearings'][sectionName]['rolling_elements'] = selectRollingElementButton
        buttonLayout.addWidget(buttonLabel)
        buttonLayout.addWidget(selectRollingElementButton)

        # Set bearing diameter subsection
        diameterSubsection = Section(self, sectionName, self.rollingElementDiameterProvided.emit)
        diameterSubsection.addWidget(createDataDisplayRow(self._outputs['Bearings'][sectionName]['di'], 'd', 'Średnica wewnętrzna łożyska', decimalPrecision=2))
        diameterSubsection.addWidget(createDataDisplayRow(self._outputs['Bearings'][sectionName]['do'], 'D', 'Średnica zewnętrzna łożyska', decimalPrecision=2))
        diameterSubsection.addWidget(createDataDisplayRow(self._outputs['Bearings'][sectionName]['drc'], 'd<sub>w</sub>', 'Obliczona średnica elementu tocznego', decimalPrecision=4))

        # Set data subsection
        dataSubsection = Section(self, sectionName, self.sectionDataProvided.emit)
        dataSubsection.addLayout(buttonLayout)
        dataSubsection.addWidget(createDataInputRow(self._inputs['Bearings'][sectionName]['f'], 'f', 'Współczynnik tarcia tocznego łożyska', decimalPrecision=5))

        # Add widgets to section layout
        sectionLayout.addWidget(diameterSubsection)
        sectionLayout.addWidget(dataSubsection)
        sectionLayout.addWidget(createDataDisplayRow(self._inputs['Bearings'][sectionName]['P'], 'P', 'Straty mocy', decimalPrecision=2))
        sectionLayout.addStretch()

        return container
    
    def _onChangeSection(self, index):
        """
        Perform actions on section change.
        """
        self.stackedSections.setCurrentIndex(index)

        # Call method onActivated for every subsection in activated section
        [section.onActivated() for section in self.stackedSections.currentWidget().findChildren(Section)]
    
    def enableSelectRollingElementButton(self, sectionName, enableButton, deleteChoice):
        """
        Enable or disable the selection button based on whether all inputs are filled.

        Args:
            sectionName (str): Specifies the bearing location.
            enableButton (bool): Specifies whether the button should be enabled or disabled.
            deleteChoice (bool): Specifies whether the button should be reset (clearing its id and data).
        """
        self._items['Bearings'][sectionName]['rolling_elements'].setEnabled(enableButton)

        if deleteChoice:
            self._items['Bearings'][sectionName]['rolling_elements'].clear()
    
    def updateSelectedRollingElement(self, sectionName, itemData):
        """
        Update selected rolling element.

        Args:
            sectionName (str): Specifies the bearing location.
            itemData (dict): Data of the selected item.
        """
        self._items['Bearings'][sectionName]['rolling_elements'].setData(itemData)
    
    def initUI(self, items, inputs, outputs):
        """
        Initialize the user interface for this tab.
        
        Args:
            items (dict): DataButtons providing storage for selected items.
            inputs (dict): Inputs.
            outputs (dict): Outputs.
        """
        self._items = items
        self._inputs = inputs
        self._outputs = outputs

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self._initSelector()
        self._initSections()
        self.mainLayout.addStretch()

        super().initUI()
