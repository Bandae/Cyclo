"""
    This file collects all functions that are common for each ITrackedTab class.
"""

from PySide2.QtWidgets import QHBoxLayout, QFrame, QSizePolicy, QLineEdit
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt

from utils.widgets.Label import Label
from .widgets.Input import Input
from .widgets.Output import Output

def _createEntrypointRow(entrypoint: QLineEdit, data: list, symbol: str, description: str, decimalPrecision: int) -> QFrame:
    """
    Create a row for data entrypoint with description, symbol, and input field.

    Args:
        entrypoint (QLineEdit): Input or Output
        data (list): List holding the attribute value and unit.
        description (str): The description of the attribute.
        symbol (str): The symbol representing the attribute.
    Returns:
        row (QFrame): row containing the created widgets.
    """
    row = QFrame()
    row.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    layout = QHBoxLayout()
    layout.setContentsMargins(5, 5, 5, 5)

    layout.setSpacing(5)
    row.setLayout(layout)

    font = QFont("Arial", 10)

    # Description label
    descriptionLabel = Label(description)
    descriptionLabel.setMinimumWidth(100)
    descriptionLabel.setWordWrap(True)
    descriptionLabel.setFont(font)

    # Symbol label
    symbolLabel = Label(symbol)
    symbolLabel.setFixedWidth(35)
    symbolLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
    symbolLabel.setAlignment(Qt.AlignmentFlag.AlignVCenter)
    symbolLabel.setFont(font)

    # Equals sign
    equalsSign = Label('=')
    equalsSign.setFixedWidth(20)
    equalsSign.setAlignment(Qt.AlignmentFlag.AlignCenter)
    equalsSign.setFont(font)

    # Entrypoint
    entrypoint.setParent(row)
    entrypoint.setDecimalPrecision(decimalPrecision)
    entrypoint.setFixedWidth(100)

    value = data[0]
    if value is not None:
        entrypoint.setValue(value)

    # Units label
    unitsLabel = Label(data[-1])
    unitsLabel.setFixedWidth(50)
    unitsLabel.setFont(font)

    # Assemble the layout
    layout.addWidget(descriptionLabel)
    layout.addWidget(symbolLabel)
    layout.addWidget(equalsSign)
    layout.addWidget(entrypoint)
    layout.addWidget(unitsLabel)

    # Save the label for later reference
    data[0] = entrypoint

    return row

def createDataInputRow(data: list, symbol: str, description: str, decimalPrecision: int=2) -> QFrame:
    input = Input()
    return _createEntrypointRow(input, data, symbol, description, decimalPrecision)

def createDataDisplayRow(data: list, symbol: str, description: str='', decimalPrecision: int=2) -> QFrame:
    output = Output()
    return _createEntrypointRow(output, data, symbol, description, decimalPrecision)

def createHeader(text, size=10, font='Arial', bold=False):
    header = Label(text)
    font = QFont(font, size)
    font.setBold(bold)
    header.setFont(font)

    return header
