from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout


class Main_View(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QStackedLayout()
        label = QLabel("Powinnno się coś kręcić ale spokojnie")
        main_layout.addWidget(label)

        self.setLayout(main_layout)