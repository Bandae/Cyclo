from functools import partial
from PySide2.QtCore import Signal, QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton

class SupportWin(QWidget):
    choiceMade = Signal(str)
    VARIANTS = [
        "jednostronnie utwierdzony",
        "utwierdzony podparty",
        "obustronnie utwierdzony",
    ]
    VARIANTS_V = [
        "Sworzeń zamocowany jednostronnie w tarczy elementu wyjściowego",
        "Sworzeń podparty i z drugiej strony zamocowany w tarczy śrubami luźno pasowanymi",
        "Sworzeń podparty i z drugiej strony zamocowany w tarczy śrubami ciasno pasowanymi",
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wybór sposobu mocowania sworzni")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(1300, 500)

        layout = QGridLayout()
        self.buttons = [
            QPushButton(icon=QIcon("resources//images//sworzen_jednostronnie_utwierdzony.png")),
            QPushButton(icon=QIcon("resources//images//sworzen_utwierdzony_podparty.png")),
            QPushButton(icon=QIcon("resources//images//sworzen_obustronnie_utwierdzony.png"))
        ]
        for ind, button in enumerate(self.buttons):
            button.setIconSize(QSize(400, 400))
            button.clicked.connect(partial(self.choiceMade.emit, self.VARIANTS[ind]))
            layout.addWidget(button, 0, ind, 9, 1)
            layout.addWidget(QLabel(self.VARIANTS_V[ind]), 10, ind, 1, 1)
            # layout.addWidget(QLabelD(self.VARIANTS_V[ind]), 10, ind, 1, 1)
        self.setLayout(layout)
