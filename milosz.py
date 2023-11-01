from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout
from widgets import AbstractTab


class Tab_Milosz(AbstractTab):
    def __init__(self, parent):
        super().__init__(parent)

        main_layout = QStackedLayout()
        label = QLabel("Tulejki tulejeczki?")
        main_layout.addWidget(label)

        self.setLayout(main_layout)
