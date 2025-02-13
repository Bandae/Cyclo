from typing import Dict, Optional
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QFrame, QGridLayout, QComboBox, QPushButton
from common.common_widgets import DoubleSpinBox, QLabelD, IntSpinBox, StatusDiodes
from .calculations import calculate_gear, get_lam_min, get_ro_min, gear_error_check


class VisualsFrame(QFrame):
    accepted = Signal(bool)

    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.filled_out = False
        self.is_accepted = False

        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        layout = QGridLayout()
        # layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.label_z = QLabelD(str(self.model.data["z"]))
        self.inputs = {
            "ro": DoubleSpinBox(self.model.data["ro"], 1, 8, 0.05),
            "lam": DoubleSpinBox(self.model.data["lam"], 0.5, 0.99, 0.005, 3),
            "g": DoubleSpinBox(self.model.data["g"], 3, 14, 0.02),
            "K": IntSpinBox(self.model.data["K"], 1, 2, 1),
        }
        for widget in self.inputs.values():
            widget.valueChanged.connect(self.changed)

        self.accept_button = QPushButton("Ok")
        self.accept_button.setEnabled(False)
        self.accept_button.clicked.connect(self.okClicked)

        layout.addWidget(QLabelD("Liczba Kół - K"), 1, 0, 1, 4)
        layout.addWidget(self.inputs["K"], 1, 4, 1, 2)
        layout.addWidget(QLabelD("Liczba Zębów - z"), 3, 0, 1, 4)
        layout.addWidget(self.label_z, 3, 4, 1, 2)
        layout.addWidget(QLabelD("Promień - ρ [mm]"), 4, 0, 1, 4)
        layout.addWidget(self.inputs["ro"], 4, 4, 1, 2)
        layout.addWidget(QLabelD("Wsp. wysokości zęba - λ"), 5, 0, 1, 4)
        layout.addWidget(self.inputs["lam"], 5, 4, 1, 2)
        layout.addWidget(QLabelD("Promień rolek - g [mm]"), 6, 0, 1, 4)
        layout.addWidget(self.inputs["g"], 6, 4, 1, 2)
        layout.addWidget(self.accept_button, 7, 5)
    
    def changed(self):
        self.is_accepted = False
        self.accepted.emit(False)
        if not all(widget.value() is not None for widget in self.inputs.values()):
            return
        
        self.filled_out = True
        for key, widget in self.inputs.items():
            self.model.data[key] = widget.value()
        
        self.afterChanges()
    
    def okClicked(self):
        # data is already written into the model when inputs are changed. (That is neccesary to calculate all wheel parameters needed for animation update)
        self.accept_button.setEnabled(False)
        self.filled_out = True
        self.is_accepted = True
        self.accepted.emit(True)
    
    def baseDataChanged(self, new_data: Dict[str, Dict[str, int]]) -> None:
        for key in new_data:
            if self.model.outside_data.get(key) is not None:
                self.model.outside_data[key] = new_data[key]
        
        self.model.data["z"] = self.model.outside_data["i"]
        self.label_z.setText(str(self.model.data["z"]))

        lam_min = get_lam_min(self.model.data["z"])
        if self.model.data["lam"] is not None:
            if lam_min > self.model.data["lam"]: self.model.data["lam"] = lam_min
        self.inputs["lam"].setMinimum(lam_min + 0.001)

        self.accepted.emit(False)
        if self.filled_out:
            self.afterChanges()
    
    def afterChanges(self):
        ro_min = get_ro_min(self.model.data["z"], self.model.data["lam"], self.model.data["g"])
        if ro_min > self.model.data["ro"]: self.model.data["ro"] = ro_min
        self.inputs["ro"].setMinimum(ro_min + 0.01)

        self.model.refillData()
        self.model.sendAnimationData()
        self.accept_button.setEnabled(True)


class ResultsFrame(QFrame):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model

        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        layout = QGridLayout()
        self.setLayout(layout)

        data_label_names = ["F_max", "p_max", "F_wzx", "F_wzy", "F_wz", "N_Ck-ri"]
        self.data_labels = { key: QLabelD(style=False) for key in data_label_names}
        self.pressure_correct_label = QLabelD("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")

        layout.addWidget(QLabelD("Max. siła międzyzębna:", style=False), 0, 0, 1, 3)
        layout.addWidget(QLabelD("F<sub>max</sub>", style=False), 1, 0, 1, 2)
        layout.addWidget(self.data_labels["F_max"], 1, 2)
        layout.addWidget(QLabelD("Max. naciski międzyzębne:", style=False), 2, 0, 1, 3)
        layout.addWidget(QLabelD("p<sub>max</sub>", style=False), 3, 0, 1, 2)
        layout.addWidget(self.data_labels["p_max"], 3, 2)
        layout.addWidget(self.pressure_correct_label, 4, 0, 1, 3)

        layout.addWidget(QLabelD("Wypadkowa siła międzyzębna:", style=False), 5, 0, 1, 3)
        layout.addWidget(QLabelD("F<sub>wzx</sub>", style=False), 6, 0, 1, 2)
        layout.addWidget(self.data_labels["F_wzx"], 6, 2)
        layout.addWidget(QLabelD("F<sub>wzy</sub>", style=False), 7, 0, 1, 2)
        layout.addWidget(self.data_labels["F_wzy"], 7, 2)
        layout.addWidget(QLabelD("F<sub>wz</sub>", style=False), 8, 0, 1, 2)
        layout.addWidget(self.data_labels["F_wz"], 8, 2)
        layout.addWidget(QLabelD("Całkowite straty mocy mechanicznej:", style=False), 9, 0, 1, 3)
        layout.addWidget(QLabelD("N<sub>Ck-ri</sub>", style=False), 10, 0, 1, 2)
        layout.addWidget(self.data_labels["N_Ck-ri"], 10, 2)
    
    def update(self):
        keys = ("F_max", "p_max", "F_wzx", "F_wzy", "F_wz", "N_Ck-ri")
        data_units = (" N", " MPa", " N", " N", " N", " W")
        for key, unit in zip(keys, data_units):
            self.data_labels[key].setText(str(self.model.data[key]) + unit)
        
        if self.model.data["p_max"] < self.model.material_data["p_dop"]:
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")
        else:
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> nie jest spełniony.")


class MaterialFrame(QFrame):
    changed = Signal()
    wheelMatChanged = Signal(dict, str)

    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setMaximumHeight(400)

        self.mat_inputs = {"wheel_mat": QComboBox(), "roller_mat": QComboBox(), "wheel_treat": QComboBox(), "roller_treat": QComboBox()}
        self.mat_inputs["wheel_mat"].addItems([mat["nazwa"] for mat in self.model.materials.values()])
        self.mat_inputs["roller_mat"].addItems([mat["nazwa"] for mat in self.model.materials.values() if mat["type"] == "steel"])
        
        self.mat_inputs["wheel_treat"].addItems(["normalizowanie", "ulepszanie cieplne", "hartowanie"])
        self.mat_inputs["roller_treat"].addItems(["normalizowanie", "ulepszanie cieplne", "hartowanie"])

        self.data_labels = { key: QLabelD(style=False) for key in ["wh_E", "wh_v", "roll_E", "roll_v"]}
        self.p_dop_label = QLabelD(style=False)

        self.mat_inputs["wheel_mat"].currentIndexChanged.connect(lambda: self.update(sendSignal=True))
        self.mat_inputs["roller_mat"].currentIndexChanged.connect(lambda: self.update())
        self.mat_inputs["wheel_treat"].currentIndexChanged.connect(lambda: self.updateTreat(sendSignal=True))
        self.mat_inputs["roller_treat"].currentIndexChanged.connect(lambda: self.updateTreat())

        self.setupLayout()
        self.update()

    def setupLayout(self):
        layout = QGridLayout()
        layout.addWidget(QLabelD("Dane materiałowe", style=False), 0, 0, 1, 6)
        layout.addWidget(QLabelD("Koło", style=False), 1, 0, 1, 2)
        layout.addWidget(self.mat_inputs["wheel_mat"], 1, 2, 1, 2)
        layout.addWidget(self.mat_inputs["wheel_treat"], 1, 4, 1, 2)
        layout.addWidget(self.data_labels["wh_E"], 2, 0, 1, 4)
        layout.addWidget(self.data_labels["wh_v"], 2, 4, 1, 2)

        layout.addWidget(QLabelD("Rolka", style=False), 3, 0, 1, 2)
        layout.addWidget(self.mat_inputs["roller_mat"], 3, 2, 1, 2)
        layout.addWidget(self.mat_inputs["roller_treat"], 3, 4, 1, 2)
        layout.addWidget(self.data_labels["roll_E"], 4, 0, 1, 4)
        layout.addWidget(self.data_labels["roll_v"], 4, 4, 1, 2)

        layout.addWidget(QLabelD("Dopuszczalny nacisk między kołem a rolką", style=False), 5, 0, 1, 4)
        layout.addWidget(self.p_dop_label, 5, 4, 1, 2)

        self.setLayout(layout)

    def update(self, sendSignal=False):
        wh_mat = self.model.material_data["wheel_mat"] = self.model.materials[self.mat_inputs["wheel_mat"].currentText()]
        roll_mat = self.model.material_data["roller_mat"] = self.model.materials[self.mat_inputs["roller_mat"].currentText()]
        wheel_treat = self.mat_inputs["wheel_treat"].currentText()
        roller_treat = self.mat_inputs["roller_treat"].currentText()

        self.mat_inputs["wheel_treat"].blockSignals(True)
        self.mat_inputs["roller_treat"].blockSignals(True)
        self.mat_inputs["wheel_treat"].clear()
        self.mat_inputs["roller_treat"].clear()
        for treat in ["normalizowanie", "ulepszanie cieplne", "hartowanie"]:
            if wh_mat.get("p_dop_" + treat):
                self.mat_inputs["wheel_treat"].addItem(treat)
            if roll_mat.get("p_dop_" + treat):
                self.mat_inputs["roller_treat"].addItem(treat)
        # zapisuje jaki byl, i jak dalej taki moze byc to ustawiam go
        if self.mat_inputs["wheel_treat"].findText(wheel_treat) != -1:
            self.mat_inputs["wheel_treat"].setCurrentText(wheel_treat)
        if self.mat_inputs["roller_treat"].findText(roller_treat) != -1:
            self.mat_inputs["roller_treat"].setCurrentText(roller_treat)
        self.mat_inputs["wheel_treat"].blockSignals(False)
        self.mat_inputs["roller_treat"].blockSignals(False)

        self.model.material_data["wheel_treat"] = self.mat_inputs["wheel_treat"].currentText()
        self.model.material_data["roller_treat"] = self.mat_inputs["roller_treat"].currentText()
        
        self.data_labels["wh_E"].setText("E: " + str(wh_mat["E"]) + " MPa")
        self.data_labels["wh_v"].setText("v: " + str(wh_mat["v"]))
        self.data_labels["roll_E"].setText("E: " + str(roll_mat["E"]) + " MPa")
        self.data_labels["roll_v"].setText("v: " + str(roll_mat["v"]))

        self.updateTreat(sendSignal)

    def updateTreat(self, sendSignal=False):
        p_dop = self.model.findAllowedPressure()
        self.p_dop_label.setText("p<sub>dop</sub> = " + str(p_dop) + " MPa")

        if sendSignal:
            self.wheelMatChanged.emit(self.model.material_data["wheel_mat"], self.model.material_data["wheel_treat"])
        self.changed.emit()

    def copyDataToInputs(self, new_input_data):
        for key in self.mat_inputs:
            self.mat_inputs[key].setCurrentText(new_input_data[key]["nazwa"])

        for key in self.other_data:
            self.data_inputs[key].setValue(new_input_data[key])
