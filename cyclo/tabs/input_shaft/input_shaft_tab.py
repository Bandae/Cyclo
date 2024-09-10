from PySide2.QtWidgets import QLabel, QStackedLayout
from tabs.common.widgets.abstract_tab import AbstractTab

class InputShaftTab(AbstractTab):
    def __init__(self):
        super().__init__()

        main_layout = QStackedLayout()
        label = QLabel("Wał wejściowy - w trakcie rozwoju ")
        main_layout.addWidget(label)

        self.setLayout(main_layout)
