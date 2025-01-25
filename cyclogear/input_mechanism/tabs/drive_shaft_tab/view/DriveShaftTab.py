from PySide2.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QStyle
from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor

from ...common.widgets.DataButton import DataButton
from ...common.widgets.ITrackedTab import ITrackedTab
from ...common.pyqt_helpers import createDataInputRow, createDataDisplayRow, createHeader

from .HelpWindow import HelpWindow

class DriveShaftTab(ITrackedTab):
    def _viewDimensionsComponent(self):
        """
        Create and layout a dimensions component.
        """
        # Create headerLayout
        headerLayout = QHBoxLayout()
        headerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Create header
        header = createHeader('Kształtowanie wału czynnego:', bold=True)

        # Create a help button
        self.helpButton = QPushButton()
        helpIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        self.helpButton.setIcon(helpIcon)
        self.helpButton.setIconSize(helpIcon.availableSizes()[0])  # Set the icon size to the available icon size
        self.helpButton.setFixedSize(self.helpButton.iconSize())  # Fit the button size to the icon size
        self.helpButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # Change cursor on hover
        self.helpButton.setStyleSheet("border: none; background-color: transparent;")

        self.helpButton.clicked.connect(self.helpWindow.show)

        headerLayout.addWidget(header)
        headerLayout.addWidget(self.helpButton)

        self.mainLayout.addLayout(headerLayout)

        self.mainLayout.addWidget(createDataDisplayRow(self._outputs['B'], 'B', 'Grubość koła obiegowego', decimalPrecision=2))
        self.mainLayout.addWidget(createDataDisplayRow(self._outputs['x'], 'x', 'Odległość pomiędzy kołami obiegowymi', decimalPrecision=2))
        self.mainLayout.addWidget(createDataDisplayRow(self._outputs['e'], 'e', 'Mimośród', decimalPrecision=2))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['L'], 'L', 'Długość wału czynnego', decimalPrecision=2))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['LA'], 'L<sub>A</sub>', 'Współrzędna podpory przesuwnej', decimalPrecision=2))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['LB'], 'L<sub>B</sub>', 'Współrzędna podpory stałej', decimalPrecision=2))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['L1'], 'L<sub>1</sub>', 'Współrzędna koła obiegowego nr 1', decimalPrecision=2))

    def _viewEccentricsComponent(self):
        self.eccentricsLayout = QVBoxLayout()

        self.mainLayout.addLayout(self.eccentricsLayout)

    def updateEccentricsComponent(self):
        # Loop backwards to remove and delete all items from the layout
        def clearLayout(layout):
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)

                # Remove the item from the layout
                layout.removeItem(item)

                # If the item is a widget, delete it
                if widget := item.widget():
                    widget.deleteLater()

        clearLayout(self.eccentricsLayout)
        for idx, input in enumerate(self._inputs['Lc'].values()):
            self.eccentricsLayout.addWidget(createDataDisplayRow(input, f'L<sub>{idx+2}</sub>', f'Współrzędne koła obiegowego nr {idx+2}', decimalPrecision=2))

    def _viewMaterialStrengthComponent(self):
        """
        Create and layout a material strength component.
        """
        self.mainLayout.addWidget(createHeader('Wytrzymałość wału czynnego:', bold=True))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['xz'], 'x<sub>z</sub>', 'Współczynnik bezpieczeństwa', decimalPrecision=1))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['qdop'], 'φ\'<sub>dop</sub>', 'Dopuszczalny jednostkowy kąt skręcenia wału', decimalPrecision=5))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['tetadop'], 'θ<sub>dop</sub>', 'Dopuszczalny kąt ugięcia wału', decimalPrecision=5))
        self.mainLayout.addWidget(createDataInputRow(self._inputs['fdop'], 'f<sub>dop</sub>', 'Dopuszczalna strzałka ugięcia wału', decimalPrecision=5))

    def _viewMaterialComponent(self):
        """
        Create and layout a material selection component.
        """
        componentLayout = QHBoxLayout()
        header = createHeader('Materiał wału czynnego:', bold=True)

        self.selectMaterialButton = DataButton('Wybierz Materiał')
        self._items['Materiał'] = self.selectMaterialButton

        componentLayout.addWidget(header)
        componentLayout.addWidget(self.selectMaterialButton)

        self.mainLayout.addLayout(componentLayout)
    
    def _initHelpDialog(self):
        self.helpWindow = HelpWindow(self)

    def updateSelectedMaterial(self, itemData):
        """
        Update the displayed material information.

        Args:
            itemData (dict): Material data.
        """
        self.selectMaterialButton.setData(itemData)

    def initUI(self, items, inputs, outputs):
        """
        Initialize the user interface for this tab.

        Args:
            items: (dict): DataButtons providing storage for selected items
            inputs (dict): Inputs
            outputs (dict): Outputs
        """
        self._items = items
        self._inputs = inputs
        self._outputs = outputs

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self._initHelpDialog()
        self._viewDimensionsComponent()
        self._viewEccentricsComponent()
        self._viewMaterialStrengthComponent()
        self._viewMaterialComponent()
        self.mainLayout.addStretch()

        super().initUI()
