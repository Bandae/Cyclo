from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QFont

class Label(QLabel):
    def __init__(self, *args, **kwargs):
        """
        Custom QLabel that applies a custom font to the label text.

        This constructor allows flexible initialization by passing any combination
        of text and parent, while ensuring the custom font is applied.
        """
        super().__init__(*args, **kwargs)

        # Set a custom font for the label text
        font = QFont('Arial', 10, QFont.Normal)
        self.setFont(font)
