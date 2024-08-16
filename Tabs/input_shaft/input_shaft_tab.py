from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout
from tabs.common.abstract_tab import AbstractTab


class InputShaftTab(AbstractTab):
    def __init__(self, parent):
        super().__init__(parent)

        main_layout = QStackedLayout()
        label = QLabel("Wałunie wałeczki ? ")
        main_layout.addWidget(label)

        self.setLayout(main_layout)
