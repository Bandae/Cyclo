from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout
from widgets import AbstractTab


class Eksport_Danych(AbstractTab):
    def __init__(self, parent):
        super().__init__(parent)

        main_layout = QStackedLayout()
        label = QLabel("Eksportujemy coś fajnego ? :D")
        main_layout.addWidget(label)

        self.setLayout(main_layout)
