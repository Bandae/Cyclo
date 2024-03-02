from PySide2.QtGui import QFont
from PySide2.QtWidgets import QDoubleSpinBox, QLabel, QFrame, QSpinBox

class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, value, minimum, maximum, step, decimal_places=2):
        super().__init__()
        self.setRange(minimum, maximum)
        self.setValue(value)
        # self.lineEdit().setReadOnly(False)
        self.setSingleStep(step)
        self.setDecimals(decimal_places)
    
    def modify(self, value=None, minimum=None, maximum=None):
        if minimum is not None:
            self.setMinimum(minimum)
        if maximum is not None:
            self.setMaximum(maximum)
        if value is not None:
            self.setValue(value)


class IntSpinBox(QSpinBox):
    def __init__(self, value, minimum, maximum, step):
        super().__init__()
        self.setRange(minimum, maximum)
        self.setValue(value)
        # self.lineEdit().setReadOnly(False)
        self.setSingleStep(step)


class QLabelD(QLabel):
    def __init__(self, text='', font_size=9, style=True):
        super().__init__()
        self.setText(str(text))
        if style:
            self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
        self.setWordWrap(True)
        self.setFont(QFont('Sans Serif', font_size))
        self.setStyleSheet("padding: 4px")
