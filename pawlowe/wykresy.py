from PySide6.QtWidgets import QTabWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QMainWindow, QWidget, QMainWindow
from PySide6.QtGui import QIcon
from pawlowe.wykres_sil import WykresSil
from pawlowe.wykres_naprezen import WykresNaprezen
import math

class Wykresy(QTabWidget):
    def __init__(self,dane,sily):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.setFixedSize(800,500)
        self.setWindowTitle("Przekładnia Cykloidalna - wykresy")
        self.showMaximized()

        # ustawienie ikonki :
        main_icon = QIcon()
        main_icon.addFile("icons//mainwindow_icon.png")
        self.setWindowIcon(main_icon)

        #tworzenie tabsów

        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabPosition(QTabWidget.North)
        self.setWindowTitle("Wykresy")

        self.tabs.addTab(WykresSil(dane,sily), "Siły")
        self.tabs.addTab(WykresNaprezen(), "Naprężenia")

        self.layout.addWidget(self.tabs)
        self.tabs.show()
        self.setLayout(self.layout)

    def exex(self):
        self.show()

