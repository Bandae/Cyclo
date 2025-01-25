from typing import Optional

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLineEdit, QWidget

class Output(QLineEdit):
    """
    Custom QLineEdit that serves as output - it is readonly and 
    allows for setting the text only programmatically.
    """

    def __init__(self, parent: QWidget = None, decimalPrecision: int = 2):
        super().__init__(parent)
        self.setReadOnly(True)
        self._maxDecimalDigits = decimalPrecision

    def setDecimalPrecision(self, decimalPrecision):
        """
        Update the maximum decimal precision of the validator.

        Args:
            decimalPrecision (int): New maximum number of decimal digits.
        """
        self._maxDecimalDigits = decimalPrecision
        self.setText(self.text())
    
    def setText(self, text: str):
        """
        Validate and set text.

        Args:
            text (str): The text to set.
        """
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        validatedText = text

        super().setText(validatedText)

    def setValue(self, value: float):
        """
        Validate and set value.

        Args:
            value (float): The value to set.
        """
        roundedValue = round(value, self._maxDecimalDigits)
        validatedText = f'{roundedValue:.{self._maxDecimalDigits}f}'
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

        super().setText(validatedText)

    def value(self) -> Optional[float]:
        """
        Return value.

        Returns:
            (float | None): The value the input is holding
        """
        text = self.text()
        return None if text == "" else float(text)
