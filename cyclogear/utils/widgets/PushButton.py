from PySide2.QtWidgets import QPushButton
from PySide2.QtGui import QFont

class PushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        """
        Custom QPushButton that applies a custom font to the button text.

        This constructor allows flexible initialization by passing any combination
        of text and parent, while ensuring the custom font is applied.
        """
        super().__init__(*args, **kwargs)

        # Set a custom font for the button text
        custom_font = QFont('Arial', 9, QFont.Normal)
        self.setFont(custom_font)
