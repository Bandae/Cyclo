from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedLayout


class Tab_Wiktor(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QStackedLayout()
        label = QLabel("Trzpienie Trzpieniunie?")
        main_layout.addWidget(label)

        self.setLayout(main_layout)

