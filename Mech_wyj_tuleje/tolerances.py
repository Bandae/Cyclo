from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QCheckBox, QButtonGroup
from common_widgets import DoubleSpinBox, QLabelD


class ToleranceInput(QWidget):
    def __init__(self, parent, label_text, tooltip_text):
        super().__init__(parent)
        self.tol = [0, 0, 0]
        self.precision = 3

        self.label = QLabelD(label_text)
        self.label.setToolTip(tooltip_text)
        self.low_input = DoubleSpinBox(self.tol[0], -0.05, 0.05, 1 * 10**-self.precision, self.precision)
        self.high_input = DoubleSpinBox(self.tol[1], -0.05, 0.05, 1 * 10**-self.precision, self.precision)
        self.deviation_input = DoubleSpinBox(self.tol[2], -0.05, 0.05, 1 * 10**-self.precision, self.precision)

        self.low_input.valueChanged.connect(self.modifiedLow)
        self.high_input.valueChanged.connect(self.modifiedHigh)
        self.deviation_input.valueChanged.connect(self.modifiedDeviation)

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.low_input, 0, 1)
        layout.addWidget(self.high_input, 0, 2)
        layout.addWidget(self.deviation_input, 0, 3)
        self.setLayout(layout)
    
    def setEnabled(self, arg__1: bool) -> None:
        super().setEnabled(arg__1)
        self.label.setEnabled(arg__1)
        self.low_input.setEnabled(arg__1)
        self.high_input.setEnabled(arg__1)
        self.deviation_input.setEnabled(arg__1)

    def modifiedLow(self):
        self.tol[0] = round(self.low_input.value(), self.precision)
        if self.tol[0] == 0:
            self.high_input.modify(minimum=0)
        else:
            self.high_input.modify(minimum=self.tol[0] + 1 * 10**-self.precision)
    
    def modifiedHigh(self):
        self.tol[1] = round(self.high_input.value(), self.precision)
        if self.tol[1] == 0:
            self.low_input.modify(maximum=0)
        else:
            self.low_input.modify(maximum=self.tol[1] - 1 * 10**-self.precision)
    
    def modifiedDeviation(self):
        self.tol[2] = round(self.deviation_input.value(), self.precision)
    
    def resetTolerances(self):
        self.low_input.blockSignals(True)
        self.high_input.blockSignals(True)
        self.low_input.modify(maximum=0)
        self.high_input.modify(minimum=0)
        self.low_input.setValue(0)
        self.high_input.setValue(0)
        self.tol[0] = 0
        self.tol[1] = 0
        self.low_input.blockSignals(False)
        self.high_input.blockSignals(False)
    
    def resetDeviations(self):
        self.deviation_input.setValue(0)
        self.tol[2] = 0
    
    def changeMode(self, mode):
        if mode == "deviations":
            self.low_input.hide()
            self.high_input.hide()
            self.deviation_input.show()
        else:
            self.low_input.show()
            self.high_input.show()
            self.deviation_input.hide()


class ToleranceEdit(QWidget):
    toleranceDataUpdated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        self.fields = {
            "T_o": ToleranceInput(self, "T<sub>o</sub>", "Tolerancja wykonania promieni otworów w kole cykloidalnym"),
            "T_t": ToleranceInput(self, "T<sub>t</sub>", "Tolerancja wykonania promieni tuleji"),
            "T_s": ToleranceInput(self, "T<sub>s</sub>", "Tolerancja wykonania promieni sworzni"),
            "T_Rk": ToleranceInput(self, "T<sub>Rk</sub>", "Tolerancja wykonania promienia rozmieszczenia otworów w kole cykloidalnym"),
            "T_Rt": ToleranceInput(self, "T<sub>Rt</sub>", "Tolerancja wykonania promienia rozmieszczenia tulei w elemencie wyjściowym"),
            "T_fi_k": ToleranceInput(self, "T<sub>\u03c6k</sub>", "Tolerancja wykonania kątowego rozmieszczenia otworów w kole cykloidalnym"),
            "T_fi_t": ToleranceInput(self, "T<sub>\u03c6t</sub>", "Tolerancja wykonania kątowego rozmieszczenia tulei w elemencie wyjściowym"),
            "T_e": ToleranceInput(self, "T<sub>e</sub>", "Tolerancja wykonania mimośrodu"),
        }
        self.labels = { key: [QLabelD(self.fields[key].label.text()), QLabelD("0"), QLabelD("0"), QLabelD("0")] for key in self.fields }
        for key in self.labels:
            self.labels[key][0].setToolTip(self.fields[key].toolTip())
        self.tolerancje = { key: widget.tol for key, widget in self.fields.items() }
        self.mode = "deviations"
        self.check = QCheckBox(text="Używaj luzów w obliczeniach")
        self.check.stateChanged.connect(self.onCheck)

        self.label_top = QLabelD("Ustaw odchyłkę:")
        self.label_bottom = QLabelD("Obecne odchyłki:")

        self.tol_check = QCheckBox(text="Wybierz pole tolerancji")
        self.dev_check = QCheckBox(text="Wybierz odchyłkę")
        self.check_group = QButtonGroup(self)
        self.check_group.addButton(self.tol_check)
        self.check_group.addButton(self.dev_check)
        self.dev_check.stateChanged.connect(self.modeChanged)
        self.tol_check.setEnabled(False)
        self.dev_check.setEnabled(False)

        self.accept_button = QPushButton(text="Ustaw odchyłki")
        self.accept_button.clicked.connect(self.dataUpdated)
        self.accept_button.setEnabled(False)

        self.reset_button = QPushButton(text="Wyzeruj odchyłki")
        def reset_fields():
            if self.tol_check.isChecked():
                for field in self.fields.values():
                    field.resetTolerances()
            else:
                for field in self.fields.values():
                    field.resetDeviations()
            self.dataUpdated()
        self.reset_button.clicked.connect(reset_fields)
        self.reset_button.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.check, 0, 0, 1, 2)
        layout.addWidget(self.tol_check, 1, 0, 1, 2)
        layout.addWidget(self.dev_check, 1, 3, 1, 2)
        layout.addWidget(self.label_top, 2, 0, 1, 4)
        for ind, widget in enumerate(self.fields.values()):
            layout.addWidget(widget.label, 3+ind-ind%2, 0 + ind%2 * 4)
            layout.addWidget(widget.low_input, 3+ind-ind%2, 1 + ind%2 * 4)
            layout.addWidget(widget.high_input, 3+ind-ind%2, 2 + ind%2 * 4)
            layout.addWidget(widget.deviation_input, 3+ind-ind%2, 1 + ind%2 * 4)
            widget.setEnabled(False)
            widget.low_input.setEnabled(False)
            widget.high_input.setEnabled(False)
            widget.deviation_input.setEnabled(False)
        layout.addWidget(self.label_bottom, 11, 0, 1, 4)
        for ind, (l1, l2, l3, l4) in enumerate(self.labels.values()):
            layout.addWidget(l1, 12+ind-ind%2, 0 + ind%2 * 4)
            layout.addWidget(l2, 12+ind-ind%2, 1 + ind%2 * 4)
            layout.addWidget(l3, 12+ind-ind%2, 2 + ind%2 * 4)
            layout.addWidget(l4, 12+ind-ind%2, 1 + ind%2 * 4)
            l2.hide()
            l3.hide()
        layout.addWidget(self.accept_button, 20, 0, 1, 2)
        layout.addWidget(self.reset_button, 20, 2, 1, 2)

        self.setLayout(layout)
        self.dev_check.setChecked(True)
        
    def onCheck(self, state):
        enable = False if state == 0 else True
        self.accept_button.setEnabled(enable)
        self.reset_button.setEnabled(enable)
        self.tol_check.setEnabled(enable)
        self.dev_check.setEnabled(enable)
        self.label_top.setEnabled(enable)
        for widget in self.fields.values():
            widget.setEnabled(enable)
            widget.low_input.setEnabled(enable)
            widget.high_input.setEnabled(enable)
            widget.deviation_input.setEnabled(enable)
            self.accept_button.setEnabled(enable)
        if enable:
            self.dataUpdated()
        else:
            self.toleranceDataUpdated.emit({"tolerances": None})
            for (_, l2, l3, l4) in self.labels.values():
                l2.setText("0")
                l3.setText("0")
                l4.setText("0")
    
    def modeChanged(self, state):
        mode = "deviations" if state == 2 else "tolerances"
        self.mode = mode
        for widget in self.fields.values():
            widget.changeMode(mode)
        if mode == "deviations":
            self.label_top.setText("Ustaw odchyłkę:")
            self.label_bottom.setText("Obecne odchyłki:")
            self.accept_button.setText("Ustaw odchyłki")
            self.reset_button.setText("Wyzeruj odchyłki")
            for (_, l2, l3, l4) in self.labels.values():
                l2.hide()
                l3.hide()
                l4.show()
        elif mode == "tolerances":
            self.label_top.setText("Ustaw pole tolerancji:")
            self.label_bottom.setText("Obecne tolerancje:")
            self.accept_button.setText("Ustaw tolerancje")
            self.reset_button.setText("Wyzeruj tolerancje")
            for (_, l2, l3, l4) in self.labels.values():
                l2.show()
                l3.show()
                l4.hide()

    def dataUpdated(self):
        for key, widget in self.fields.items():
            for ind in range(3):
                temp_text = str(widget.tol[ind]) if widget.tol[ind] <= 0 else "+" + str(widget.tol[ind])
                self.labels[key][ind+1].setText(temp_text)
        self.toleranceDataUpdated.emit({"tolerances": {key: val[2] if self.mode == "deviations" else [val[0], val[1]] for key, val in self.tolerancje.items()}})
    
    def copyDataToInputs(self, new_tolerances):
        for key, widget in self.fields.items():
            widget.low_input.setValue(new_tolerances[key][0])
            widget.high_input.setValue(new_tolerances[key][1])
            widget.deviation_input.setValue(new_tolerances[key][2])
