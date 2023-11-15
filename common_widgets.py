from PySide2.QtWidgets import QDoubleSpinBox, QLabel, QFrame, QSpinBox

class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, value, minimum, maximum, step, decimal_places=2):
        super().__init__()
        self.setValue(value)
        self.lineEdit().setReadOnly(False)
        self.setRange(minimum, maximum)
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
        self.setValue(value)
        self.lineEdit().setReadOnly(False)
        self.setRange(minimum, maximum)
        self.setSingleStep(step)


class QLabelD(QLabel):
    def __init__(self,a):
        super().__init__()
        self.setText(str(a))
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
