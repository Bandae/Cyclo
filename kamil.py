from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout
from abstract_tab import AbstractTab


class Tab_Kamil(AbstractTab):
    def __init__(self, parent):
        super().__init__(parent)

        main_layout = QStackedLayout()
        label = QLabel("Wałunie wałeczki ? ")
        main_layout.addWidget(label)

        self.setLayout(main_layout)
