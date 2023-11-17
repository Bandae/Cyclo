from PySide2.QtWidgets import QLabel, QGridLayout, QStackedLayout, QPushButton
from abstract_tab import AbstractTab


class Eksport_Danych(AbstractTab):
    def __init__(self, parent, sily):
        super().__init__(parent)
        main_layout = QGridLayout()

        pavel01 = QPushButton("Przekładnia Cykloidalna")
        self.pavel11 = QPushButton("TO CSV")

        self.pavel11.clicked.connect(lambda: self.paveltocsv(sily))
        pavel12 = QPushButton("TO DXF")
        pavel12.clicked.connect(lambda: self.paveltocsv(sily))
        pavel13 = QPushButton("inny ??")

        wiktor01 = QPushButton("Mechanizm wyjsciowy I")
        wiktor11 = QPushButton("TO CSV")
        wiktor12 = QPushButton("TO DXF")
        wiktor13 = QPushButton("inny ??")

        milosz01 = QPushButton("Mechanizm wyjsciowy II")
        milosz11 = QPushButton("TO CSV")
        milosz12 = QPushButton("TO DXF")
        milosz13 = QPushButton("inny ??")

        kamil01 = QPushButton("Układ Wejsciowy")
        kamil11 = QPushButton("TO CSV")
        kamil12 = QPushButton("TO DXF")
        kamil13 = QPushButton("inny ??")

        all01 = QPushButton("Calosciowy eksport")
        all11 = QPushButton("TO CSV")
        all12 = QPushButton("TO DXF")
        all13 = QPushButton("inny ??")

        main_layout.addWidget(pavel01, 0, 0)
        main_layout.addWidget(self.pavel11,0,1)
        main_layout.addWidget(pavel12, 0, 2)
        main_layout.addWidget(pavel13, 0, 3)

        main_layout.addWidget(wiktor01, 1, 0)
        main_layout.addWidget(wiktor11, 1, 1)
        main_layout.addWidget(wiktor12, 1, 2)
        main_layout.addWidget(wiktor13, 1, 3)

        main_layout.addWidget(milosz01, 2, 0)
        main_layout.addWidget(milosz11, 2, 1)
        main_layout.addWidget(milosz12, 2, 2)
        main_layout.addWidget(milosz13, 2, 3)

        main_layout.addWidget(kamil01, 3, 0)
        main_layout.addWidget(kamil11, 3, 1)
        main_layout.addWidget(kamil12, 3, 2)
        main_layout.addWidget(kamil13, 3, 3)

        main_layout.addWidget(all01, 4, 0)
        main_layout.addWidget(all11, 4, 1)
        main_layout.addWidget(all12, 4, 2)
        main_layout.addWidget(all13, 4, 3)

        self.setLayout(main_layout)

    def paveltocsv(self,sily):
        for i in range(len(sily)):
            print(sily[i])
