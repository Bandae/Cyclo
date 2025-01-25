from PySide2.QtWidgets import QVBoxLayout, QScrollArea, QWidget, QFrame
from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette

from ...common.widgets.ITrackedTab import ITrackedTab
from ...common.pyqt_helpers import createDataDisplayRow, createHeader

class ResultsTab(ITrackedTab):
    def _viewResultsSection(self):
        contentWidget = QWidget()
        contentLayout = QVBoxLayout()
        contentWidget.setLayout(contentLayout)

        scrollArea = QScrollArea()
        scrollArea.setContentsMargins(0, 0, 0, 0)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrollArea.verticalScrollBar().setStyleSheet("""
        QScrollBar:vertical {
            border: none;
            background: white;
            width: 13px;
            margin: 10px 0 10px 0;
        }
        QScrollBar::handle:vertical {
            background: #b5b5b5;
            min-height: 20px;
            max-height: 80px;
            border-radius: 4px;
            width: 8px;
            margin-right: 5px
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;  /* Removes the buttons */
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        """)

        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(contentWidget)

        # Remove the border from QScrollArea
        scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        scrollArea.setFrameShadow(QFrame.Shadow.Plain)

        # Match the background color of the QScrollArea to the QTabWidget
        palette = scrollArea.palette()
        palette.setColor(QPalette.ColorRole.Window, self.palette().color(QPalette.ColorRole.Base))
        scrollArea.setPalette(palette)
        scrollArea.setAutoFillBackground(True)

        self.mainLayout.addWidget(scrollArea)

        contentLayout.addWidget(createHeader('Ogólne:', bold=True))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['nwe'], 'n<sub>we</sub>', 'Wejściowa prędkość obrotowa', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['Mwe'], 'M<sub>we</sub>', 'Wejściowy moment obrotowy', decimalPrecision=2))
        contentLayout.addWidget(createHeader('Wymiary wału:', bold=True))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['L'], 'L', 'Długość wału czynnego', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['LA'], 'L<sub>A</sub>', 'Współrzędna podpory przesuwnej', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['LB'], 'L<sub>B</sub>', 'Współrzędna podpory stałej', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['L1'], 'L<sub>1</sub>', 'Współrzędna koła obiegowego nr 1', decimalPrecision=2))
        for idx, input in enumerate(self._outputs['Lc'].values()):
            contentLayout.addWidget(createDataDisplayRow(input, f'L<sub>{idx+2}</sub>', f'Współrzędna koła obiegowego nr {idx+2}', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['e'], 'e', 'Mimośród', decimalPrecision=2))
        contentLayout.addWidget(createHeader('Siły i reakcje:', bold=True))
        for idx, input in enumerate(self._outputs['Fx'].values()):
            contentLayout.addWidget(createDataDisplayRow(input, f'R<sub>{idx+1}</sub>', f'Siła wywierana ze strony koła obiegowego nr {idx+1}', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['Ra'], 'R<sub>A</sub>', 'Reakcja podpory przesuwnej A', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['Rb'], 'R<sub>B</sub>', 'Reakcja podpory stałej B', decimalPrecision=2))
        contentLayout.addWidget(createHeader('Straty mocy w łożyskach:', bold=True))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['Bearings']['support_A']['P'], 'P<sub>A</sub>', 'Podpora przesuwna A', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['Bearings']['support_B']['P'], 'P<sub>B</sub>', 'Podpora stała B', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['Bearings']['eccentrics']['P'], 'P<sub>e</sub>', 'Mimośrody', decimalPrecision=2))
        contentLayout.addWidget(createDataDisplayRow(self._outputs['P'], 'P<sub>c</sub>', 'Całkowite straty mocy', decimalPrecision=2))
        contentLayout.addStretch()

    def initUI(self, outputs):
        """
        Initialize the user interface for ResultsTab.

        Args:
            outputs (dict): Outputs
        """
        self._outputs = outputs

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins from tab2_layout
        self.mainLayout.setSpacing(0)

        self._viewResultsSection()
        super().initUI()
