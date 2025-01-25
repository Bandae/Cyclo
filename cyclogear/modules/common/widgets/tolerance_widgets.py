from typing import Dict, List, Tuple
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QCheckBox, QButtonGroup
from common_widgets import DoubleSpinBox, QLabelD

# TODO: min i max na polach w toleranceinput


class ToleranceInput(QWidget):
    '''Widżet do wprowadzania wartości tolerancji dla jednej wartości.
    
    Wyświetla dwa pola (na wprowadzenie dolnej i górnej odchyłki) w trybie pól tolerancji
    lub jedno (na odchyłkę) w trybie wprowadzania konkretnych odchyłek.
    '''

    def __init__(self, parent: QWidget, label_text: str, tooltip_text: str) -> None:
        super().__init__(parent)
        self.tol = [0.0, 0.0, 0.0]
        self.precision = 3

        self.label = QLabelD(label_text)
        self.label.setToolTip(tooltip_text)
        self.low_input = DoubleSpinBox(self.tol[0], -1, 1, 1 * 10**-self.precision, self.precision)
        self.high_input = DoubleSpinBox(self.tol[1], -1, 1, 1 * 10**-self.precision, self.precision)
        self.deviation_input = DoubleSpinBox(self.tol[2], -1, 1, 1 * 10**-self.precision, self.precision)

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

    def modifiedLow(self) -> None:
        self.tol[0] = round(self.low_input.value(), self.precision)
        if self.tol[0] == 0:
            self.high_input.modify(minimum=0)
        else:
            self.high_input.modify(minimum=self.tol[0] + 1 * 10**-self.precision)
    
    def modifiedHigh(self) -> None:
        self.tol[1] = round(self.high_input.value(), self.precision)
        if self.tol[1] == 0:
            self.low_input.modify(maximum=0)
        else:
            self.low_input.modify(maximum=self.tol[1] - 1 * 10**-self.precision)
    
    def modifiedDeviation(self) -> None:
        self.tol[2] = round(self.deviation_input.value(), self.precision)
    
    def resetTolerances(self) -> None:
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
    
    def resetDeviations(self) -> None:
        self.deviation_input.setValue(0)
        self.tol[2] = 0
    
    def changeMode(self, mode: str) -> None:
        if mode == "deviations":
            self.low_input.hide()
            self.high_input.hide()
            self.deviation_input.show()
        else:
            self.low_input.show()
            self.high_input.show()
            self.deviation_input.hide()


class ToleranceEdit(QWidget):
    '''Widżet obsługujący wprowadzanie tolerancji wykonania elementów dla zakładki.
    
    Zawiera wyznaczoną przy tworzeniu ilość pól ToleranceInput.
    Możliwość wyboru trybu pól tolerancji lub konkretnej odchyłki, reset wartości, wyłączenie widżetu.
    Zatwierdzenie zmian wysyła sygnał toleranceDataUpdated z słownikiem wartości odchyłek (Dict[str, float]),
    lub pól tolerancji Dict[str, Tuple[float, float]].
    Wyłączenie widżetu przyciskiem self.check wysyła sygnał toleranceDataUpdated(None).
    '''
    # https://doc.qt.io/qtforpython-6/tutorials/basictutorial/signals_and_slots.html#overloading-signals-and-slots
    toleranceDataUpdated = Signal((dict,), (None,))

    def __init__(self, parent: QWidget, fields: Tuple[Tuple[str, str, str], ...]) -> None:
        '''Jako argument fields należy podać zestawy nazw dla pożądanych parametrów tolerancji:
        - skrót do użycia jako klucz (z podkreśleniami),
        - skrót do wyświetlania w UI (dopuszczalne RTF/tagi html),
        - pełna nazwa.

        Przykład:
        (("T_s", "T<sub>s</sub>", "Tolerancja wykonania promieni sworzni"), ...)
        '''

        super().__init__(parent)
        self.fields = { field[0]: ToleranceInput(self, field[1], field[2]) for field in fields}
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
        
    def onCheck(self, state: int) -> None:
        enable = True if state else False
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
            self.toleranceDataUpdated.emit(None)
            for (_, l2, l3, l4) in self.labels.values():
                l2.setText("0")
                l3.setText("0")
                l4.setText("0")
    
    def modeChanged(self, state: int) -> None:
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

    def dataUpdated(self) -> None:
        for key, widget in self.fields.items():
            for i in range(3):
                temp_text = str(widget.tol[i]) if widget.tol[i] <= 0 else "+" + str(widget.tol[i])
                self.labels[key][i+1].setText(temp_text)
        self.toleranceDataUpdated.emit({key: val[2] if self.mode == "deviations" else (val[0], val[1]) for key, val in self.tolerancje.items()})
    
    def saveData(self) -> Dict[str, Tuple[float, float, float]]:
        return {key: (val[0], val[1], val[2]) for key, val in self.tolerancje.items()}

    def copyDataToInputs(self, new_tolerances: Dict[str, Tuple[float, float, float]]) -> None:
        for key, widget in self.fields.items():
            widget.low_input.setValue(new_tolerances[key][0])
            widget.high_input.setValue(new_tolerances[key][1])
            widget.deviation_input.setValue(new_tolerances[key][2])
