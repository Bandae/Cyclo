from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout

class Eksport_Danych(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QStackedLayout()
        label = QLabel("Eksportujemy coś fajnego ? :D")
        main_layout.addWidget(label)

        self.setLayout(main_layout)
