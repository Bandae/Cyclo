from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout

class Tab_Kamil(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QStackedLayout()
        label = QLabel("Wałunie wałeczki ? ")
        main_layout.addWidget(label)

        self.setLayout(main_layout)

