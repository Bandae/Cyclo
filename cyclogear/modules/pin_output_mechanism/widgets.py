from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGridLayout, QComboBox, QFrame, QPushButton
from common.common_widgets import QLabelD, DoubleSpinBox, IntSpinBox


class VisualsFrame(QFrame):
    accepted = Signal(bool)

    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.filled_out = False
        self.is_accepted = False

        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        layout = QGridLayout()
        self.setLayout(layout)

        self.n_input = IntSpinBox(self.model.input_dane["n"], 4, 28, 1)
        self.n_input.valueChanged.connect(self.changed)
        self.Rwt_input = DoubleSpinBox(self.model.input_dane["R_wt"], 20, 300, 1, 1)
        self.Rwt_input.valueChanged.connect(self.changed)

        self.accept_button = QPushButton("Ok")
        self.accept_button.setEnabled(False)
        self.accept_button.clicked.connect(self.okClicked)

        n_label = QLabelD("Liczba sworzni [n]")
        layout.addWidget(n_label, 0, 0, 1, 2)
        layout.addWidget(self.n_input, 0, 2, 1, 2)
        lab_Rwt = QLabelD("R<sub>wt</sub> [mm]")
        lab_Rwt.setToolTip("Promień rozmieszczenia sworzni")
        layout.addWidget(lab_Rwt, 1, 0)
        layout.addWidget(self.Rwt_input, 1, 1)
        name_Rwk = QLabelD("R<sub>wk</sub>")
        name_Rwk.setToolTip("Promień rozmieszczenia otworów w kole cykloidalnym")
        layout.addWidget(name_Rwk, 1, 2)
        self.Rwk_label = QLabelD("")
        layout.addWidget(self.Rwk_label, 1, 3)
        layout.addWidget(self.accept_button, 2, 3)
    
    def changed(self):
        self.is_accepted = False
        n, R_wt = self.n_input.value(), self.Rwt_input.value()
        self.accepted.emit(False)
        if n is not None and R_wt is not None:
            self.model.sendAnimationUpdates(n, R_wt)
            self.accept_button.setEnabled(True)
        if R_wt is not None:
            self.Rwk_label.setText(str(self.Rwt_input.value()) + " mm")
    
    def okClicked(self):
        self.model.input_dane["n"] = self.n_input.value()
        self.model.input_dane["R_wt"] = self.Rwt_input.value()
        self.accept_button.setEnabled(False)
        self.filled_out = True
        self.is_accepted = True
        self.accepted.emit(True)


class ResultsFrame(QFrame):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model

        layout = QGridLayout()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        data_label_names = ["F_max", "p_max", "F_wmr", "r_mr", "N_cmr"]
        self.data_labels = { key: QLabelD(style=False) for key in data_label_names}
        self.pressure_correct_label = QLabelD("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")

        layout.addWidget(QLabelD("Max. siła działająca na sworzeń:", style=False), 0, 0, 1, 3)
        layout.addWidget(QLabelD("F<sub>max</sub>", style=False), 1, 0, 1, 2)
        layout.addWidget(self.data_labels["F_max"], 1, 2)
        layout.addWidget(QLabelD("Max. naciski między kołem a tuleją:", style=False), 2, 0, 1, 3)
        layout.addWidget(QLabelD("p<sub>max</sub>", style=False), 3, 0, 1, 2)
        layout.addWidget(self.data_labels["p_max"], 3, 2)
        layout.addWidget(self.pressure_correct_label, 4, 0, 1, 3)

        layout.addWidget(QLabelD("Wypadkowa siła działająca na sworznie:", style=False), 5, 0, 1, 3)
        layout.addWidget(QLabelD("F<sub>wmr</sub>", style=False), 6, 0, 1, 2)
        layout.addWidget(self.data_labels["F_wmr"], 6, 2)
        layout.addWidget(QLabelD("Ramię działania siły wypadkowej:", style=False), 7, 0, 1, 3)
        layout.addWidget(QLabelD("r<sub>mr</sub>", style=False), 8, 0, 1, 2)
        layout.addWidget(self.data_labels["r_mr"], 8, 2)
        layout.addWidget(QLabelD("Całkowite straty mocy mechanicznej:", style=False), 9, 0, 1, 3)
        layout.addWidget(QLabelD("N<sub>Cmr</sub>", style=False), 10, 0, 1, 2)
        layout.addWidget(self.data_labels["N_cmr"], 10, 2)

        self.setLayout(layout)
    
    def update(self):
        if self.model.obliczone_dane["p_max"] < self.model.material_data["p_dop"]:
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")
        else:
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> nie jest spełniony.")
        
        keys = ("F_max", "p_max", "F_wmr", "r_mr", "N_cmr")
        data_units = (" N", " MPa", " N", " mm", " W")
        for key, unit in zip(keys, data_units):
            self.data_labels[key].setText(str(self.model.obliczone_dane[key]) + unit)


class MaterialsFrame(QFrame):
    updated = Signal()

    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model

        layout = QGridLayout()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        self.data_inputs = {"sw_mat": QComboBox(), "tul_mat": QComboBox(), "tul_treat": QComboBox()}
        # TODO: zamienić na używanie bazy danych.
        self.data_inputs["sw_mat"].addItems([mat["nazwa"] for mat in self.model.materials.values() if mat["use"] == "pin" or mat["use"] == "both"])
        self.data_inputs["tul_mat"].addItems([mat["nazwa"] for mat in self.model.materials.values() if mat["use"] == "sleeve" or mat["use"] == "both"])
        self.data_inputs["tul_treat"].addItems(["normalizowanie", "ulepszanie cieplne", "hartowanie"])
        self.data_inputs["sw_mat"].currentIndexChanged.connect(self.update)
        self.data_inputs["tul_mat"].currentIndexChanged.connect(self.update)
        self.data_inputs["tul_treat"].currentIndexChanged.connect(self.updateAllowedPressure)
        self.coef_input = DoubleSpinBox(self.model.material_data["pin_safety_coef"], 1, 2.5, 0.1)
        self.coef_input.valueChanged.connect(self.update)
        data_label_names = ["pin_re", "tul_E", "tul_v", "wh_name", "wh_treat", "wh_E", "wh_v", "p_dop"]
        self.data_labels = { key: QLabelD(style=False) for key in data_label_names}

        layout.addWidget(QLabelD("Dane materiałowe", style=False), 0, 0, 1, 6)
        layout.addWidget(QLabelD("Sworzeń", style=False), 1, 0, 1, 2)
        layout.addWidget(self.data_inputs["sw_mat"], 1, 2, 1, 2)
        layout.addWidget(self.data_labels["pin_re"], 2, 0, 1, 3)
        coef_label = QLabelD('k', style=False)
        coef_label.setToolTip('Współczynnik bezpieczeńswa zginania sworznia')
        layout.addWidget(coef_label, 2, 4)
        layout.addWidget(self.coef_input, 2, 5)

        layout.addWidget(QLabelD("Tuleja", style=False), 3, 0, 1, 2)
        layout.addWidget(self.data_inputs["tul_mat"], 3, 2, 1, 2)
        layout.addWidget(self.data_inputs["tul_treat"], 3, 4, 1, 2)
        layout.addWidget(self.data_labels["tul_E"], 5, 0, 1, 3)
        layout.addWidget(self.data_labels["tul_v"], 5, 4, 1, 2)

        layout.addWidget(QLabelD("Koło", style=False), 6, 0, 1, 2)
        layout.addWidget(self.data_labels["wh_name"], 6, 2, 1, 2)
        layout.addWidget(self.data_labels["wh_treat"], 6, 4, 1, 2)
        layout.addWidget(self.data_labels["wh_E"], 7, 0, 1, 3)
        layout.addWidget(self.data_labels["wh_v"], 7, 4, 1, 2)

        layout.addWidget(QLabelD("Dopuszczalny nacisk między kołem a tuleją", style=False), 8, 0, 1, 3)
        layout.addWidget(self.data_labels["p_dop"], 8, 4, 1, 2)

        self.setLayout(layout)
        self.update()
        self.changeWheelMat(self.model.material_data["wheel_mat"], "normalizowanie")

    def changeWheelMat(self, new_mat, new_treat):
        self.model.material_data["wheel_mat"] = new_mat
        self.model.material_data["wheel_treat"] = new_treat

        self.data_labels["wh_name"].setText(str(new_mat["nazwa"]))
        self.data_labels["wh_treat"].setText(new_treat)
        self.data_labels["wh_E"].setText("E: " + str(new_mat["E"]) + " MPa")
        self.data_labels["wh_v"].setText("v: " + str(new_mat["v"]))

        self.updateAllowedPressure()

    def update(self):
        sw_mat = self.model.materials[self.data_inputs["sw_mat"].currentText()]
        tul_mat = self.model.materials[self.data_inputs["tul_mat"].currentText()]
        tul_treat = self.data_inputs["tul_treat"].currentText()
        self.model.material_data["pin_mat"] = sw_mat
        self.model.material_data["sleeve_mat"] = tul_mat
        self.model.material_data["pin_safety_coef"] = self.coef_input.value()

        self.data_inputs["tul_treat"].blockSignals(True)
        self.data_inputs["tul_treat"].clear()
        for treat in ["normalizowanie", "ulepszanie cieplne", "hartowanie"]:
            if tul_mat.get("p_dop_" + treat):
                self.data_inputs["tul_treat"].addItem(treat)
        if self.data_inputs["tul_treat"].findText(tul_treat) != -1:
            # keep the treat option as it was, if it is available for the new material
            self.data_inputs["tul_treat"].setCurrentText(tul_treat)
            self.model.material_data["sleeve_treat"] = tul_treat
        elif self.data_inputs["tul_treat"].count() != 0:
            # if not available, update to the now displayed treat
            self.model.material_data["sleeve_treat"] = self.data_inputs["tul_treat"].currentText()
        else:
            # if no available treat for the new material, update treat to None
            self.model.material_data["sleeve_treat"] = None
        self.data_inputs["tul_treat"].blockSignals(False)

        self.data_labels["pin_re"].setText("Re: " + str(sw_mat["Re"]) + " MPa")
        self.data_labels["tul_E"].setText("E: " + str(tul_mat["E"]) + " MPa")
        self.data_labels["tul_v"].setText("v: " + str(tul_mat["v"]))

        self.updateAllowedPressure()
    
    def updateAllowedPressure(self):
        self.model.findAllowedPressure()
        self.data_labels["p_dop"].setText("p<sub>dop</sub> = " + str(self.model.material_data["p_dop"]) + " MPa")
        self.updated.emit()

    def loadData(self, new_material_data):
        self.coef_input.blockSignals(True)
        self.coef_input.setValue(new_material_data["pin_sft_coef"])
        self.coef_input.blockSignals(False)
        self.model.material_data["wheel_mat"] = new_material_data["wheel"]
        for key in self.data_inputs:
            self.data_inputs[key].blockSignals(True)
            self.data_inputs[key].setCurrentText(new_material_data[key]["nazwa"])
            self.data_inputs[key].blockSignals(False)
        self.update()
