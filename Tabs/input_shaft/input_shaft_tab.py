from PySide2.QtWidgets import QLabel, QStackedLayout
from tabs.common.widgets.abstract_tab import AbstractTab

class InputShaftTab(AbstractTab):
    def __init__(self, parent):
        super().__init__(parent)

        main_layout = QStackedLayout()
        label = QLabel("Wał wejściowy - w trakcie rozwoju ")
        main_layout.addWidget(label)

        self.setLayout(main_layout)
