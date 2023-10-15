from PySide6.QtWidgets import QDialog
import math

class Wykresy(QDialog):
    def __init__(self):
        super().__init__()

        self.setFixedSize(200,200)
        self.setWindowTitle("Wykresy")


