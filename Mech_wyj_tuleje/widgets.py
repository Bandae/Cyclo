from PySide2.QtWidgets import QGridLayout, QComboBox, QFrame
from common_widgets import QLabelD, DoubleSpinBox

# TODO: Dodać jednostke do E
class ResultsFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QGridLayout()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        data_label_names = ["F_max", "p_max", "F_wmr", "r_mr", "N_cmr"]
        self.data_labels = { key: QLabelD(style=False) for key in data_label_names}
        self.pressure_correct_label = QLabelD("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")

        fmax_label = QLabelD("F<sub>max</sub>", style=False)
        layout.addWidget(fmax_label, 0, 0, 1, 2)
        layout.addWidget(self.data_labels["F_max"], 0, 2)
        pmax_label = QLabelD("p<sub>max</sub>", style=False)
        layout.addWidget(pmax_label, 1, 0, 1, 2)
        layout.addWidget(self.data_labels["p_max"], 1, 2)
        layout.addWidget(self.pressure_correct_label, 2, 0, 1, 3)

        fwmr_label = QLabelD("F<sub>wmr</sub>", style=False)
        layout.addWidget(fwmr_label, 3, 0, 1, 2)
        layout.addWidget(self.data_labels["F_wmr"], 3, 2)
        rmr_label = QLabelD("r<sub>mr</sub>", style=False)
        layout.addWidget(rmr_label, 4, 0, 1, 2)
        layout.addWidget(self.data_labels["r_mr"], 4, 2)
        ncmr_label = QLabelD("N<sub>Cmr</sub>", style=False)
        layout.addWidget(ncmr_label, 5, 0, 1, 2)
        layout.addWidget(self.data_labels["N_cmr"], 5, 2)

        self.setLayout(layout)
    
    def update(self, new_data, p_dop):
        data_units = [" N", " MPa", " N", " mm", " W"]
        for index, (key, new_value) in enumerate(new_data.items()):
            self.data_labels[key].setText(str(new_value) + data_units[index])
        if new_data["p_max"] < p_dop: 
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")
        else:
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> nie jest spełniony.")


class MaterialsFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QGridLayout()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        self.materials = {
            "15HN": {"nazwa": "15HN", "type": "steel", "E": 210000, "v": 0.3, "Re": 850, "use": "pin"},
            "16HG": {"nazwa": "16HG", "type": "steel", "E": 210000, "v": 0.3, "Re": 850, "use": "pin"},
            "40HM": {"nazwa": "40HM", "type": "steel", "E": 210000, "v": 0.3, "Re": 900, "use": "pin"},
            "34HNM": {"nazwa": "34HNM", "type": "steel", "E": 210000, "v": 0.3, "Re": 1000, "use": "pin"},
            "C45": {"nazwa": "C45", "type": "steel", "E": 210000, "v": 0.3, "Re": 710, "p_dop_normalizowanie": 550, "p_dop_ulepszanie cieplne": 700, "p_dop_hartowanie": 1300, "use": "both"},
            "C55": {"nazwa": "C55", "type": "steel", "E": 210000, "v": 0.3, "Re": 810, "p_dop_normalizowanie": 600, "p_dop_ulepszanie cieplne": 900, "p_dop_hartowanie": 1500, "use": "both"},
            "B 101": {"nazwa": "B 101", "type": "bronze", "E": 117000, "v": 0.34, "use": "sleeve"},
            "B 102": {"nazwa": "B 102", "type": "bronze", "E": 117000, "v": 0.34, "use": "sleeve"},
            "BA 1044": {"nazwa": "BA 1044", "type": "bronze", "E": 117000, "v": 0.34, "use": "sleeve"},
            "C30": {"nazwa": "C30", "type": "steel", "E": 210000, "v": 0.3, "p_dop_normalizowanie": 450, "p_dop_ulepszanie cieplne": 550, "p_dop_hartowanie": 1000, "use": "sleeve"},
            "50G": {"nazwa": "50G", "type": "steel", "E": 210000, "v": 0.3, "p_dop_ulepszanie cieplne": 900, "p_dop_hartowanie": 1450, "use": "sleeve"},
            "40H": {"nazwa": "40H", "type": "steel", "E": 210000, "v": 0.3, "p_dop_ulepszanie cieplne": 1000, "p_dop_hartowanie": 1550, "use": "sleeve"},
            "40HN": {"nazwa": "40HN", "type": "steel", "E": 210000, "v": 0.3, "p_dop_ulepszanie cieplne": 1000, "p_dop_hartowanie": 1600, "use": "sleeve"},
        }
        self.pin_sft_coef = 2
        self.current_mats = {"pin": self.materials["15HN"], "sleeve": self.materials["C45"], "wheel": self.materials["C30"], "wheel_treat": "normalizowanie"}
        self.data_inputs = {"sw_mat": QComboBox(), "tul_mat": QComboBox(), "tul_treat": QComboBox()}
        self.data_inputs["sw_mat"].addItems([mat["nazwa"] for mat in self.materials.values() if mat["use"] == "pin" or mat["use"] == "both"])
        self.data_inputs["tul_mat"].addItems([mat["nazwa"] for mat in self.materials.values() if mat["use"] == "sleeve" or mat["use"] == "both"])
        self.data_inputs["tul_treat"].addItems(["normalizowanie", "ulepszanie cieplne", "hartowanie"])
        self.data_inputs["sw_mat"].currentIndexChanged.connect(self.update)
        self.data_inputs["tul_mat"].currentIndexChanged.connect(self.update)
        self.data_inputs["tul_treat"].currentIndexChanged.connect(self.updateTreat)
        self.coef_input = DoubleSpinBox(self.pin_sft_coef, 1, 2.5, 0.1)
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
        self.changeWheelMat(self.current_mats["wheel"], "normalizowanie")
    
    def getAllowedPressure(self) -> int:
        wheel_material = self.current_mats["wheel"]
        sleeve_material = self.current_mats["sleeve"]
        sleeve_treat = self.data_inputs["tul_treat"].currentText()
        wheel_treat = self.current_mats["wheel_treat"]
        wheel_tempered = wheel_material["type"] == "steel" and wheel_treat == "ulepszanie cieplne"

        if sleeve_material["nazwa"] == "B 101" and wheel_tempered:
            return 320
        elif sleeve_material["nazwa"] == "B 101" and not wheel_tempered:
            return 210
        elif sleeve_material["nazwa"] == "B 102" and wheel_tempered:
            return 320
        elif sleeve_material["nazwa"] == "B 102" and not wheel_tempered:
            return 215
        elif sleeve_material["nazwa"] == "BA 1044" and wheel_tempered:
            return 495
        elif sleeve_material["nazwa"] == "BA 1044" and not wheel_tempered:
            return 330
        else:
            wheel_p_dop = self.current_mats["wheel"]["p_dop_" + wheel_treat]
            sleeve_p_dop = self.current_mats["sleeve"]["p_dop_" + sleeve_treat]
            return min(sleeve_p_dop, wheel_p_dop)
    
    def getData(self):
        copy = self.current_mats.copy()
        copy.update({"p_dop": int(self.data_labels["p_dop"].text().replace(" MPa", "")), "pin_sft_coef": self.pin_sft_coef})
        return copy

    def changeWheelMat(self, new_mat, new_treat):
        self.current_mats["wheel"] = new_mat
        self.current_mats["wheel_treat"] = new_treat
        self.data_labels["wh_name"].setText(str(new_mat["nazwa"]))
        self.data_labels["wh_treat"].setText(new_treat)
        self.data_labels["wh_E"].setText("E: " + str(new_mat["E"]) + " MPa")
        self.data_labels["wh_v"].setText("v: " + str(new_mat["v"]))
        p_dop = self.getAllowedPressure()
        self.data_labels["p_dop"].setText(str(p_dop) + " MPa")

    def update(self):
        sw_mat = self.materials[self.data_inputs["sw_mat"].currentText()]
        tul_mat = self.materials[self.data_inputs["tul_mat"].currentText()]
        self.current_mats["pin"] = sw_mat
        self.current_mats["sleeve"] = tul_mat
        self.pin_sft_coef = self.coef_input.value()

        self.data_inputs["tul_treat"].blockSignals(True)
        tul_treat = self.data_inputs["tul_treat"].currentText()
        self.data_inputs["tul_treat"].clear()
        for treat in ["normalizowanie", "ulepszanie cieplne", "hartowanie"]:
            if tul_mat.get("p_dop_" + treat):
                self.data_inputs["tul_treat"].addItem(treat)
        if self.data_inputs["tul_treat"].findText(tul_treat) != -1:
            self.data_inputs["tul_treat"].setCurrentText(tul_treat)
        self.data_inputs["tul_treat"].blockSignals(False)

        self.data_labels["pin_re"].setText("Re: " + str(sw_mat["Re"]) + " MPa")
        self.data_labels["tul_E"].setText("E: " + str(tul_mat["E"]) + " MPa")
        self.data_labels["tul_v"].setText("v: " + str(tul_mat["v"]))
        p_dop = self.getAllowedPressure()
        self.data_labels["p_dop"].setText(str(p_dop) + " MPa")
    
    def updateTreat(self):
        p_dop = self.getAllowedPressure()
        self.data_labels["p_dop"].setText(str(p_dop) + " MPa")

    def loadData(self, new_material_data):
        self.coef_input.blockSignals(True)
        self.coef_input.setValue(new_material_data["pin_sft_coef"])
        self.coef_input.blockSignals(False)
        self.current_mats["wheel"] = new_material_data["wheel"]
        for key in self.data_inputs:
            self.data_inputs[key].blockSignals(True)
            self.data_inputs[key].setCurrentText(new_material_data[key]["nazwa"])
            self.data_inputs[key].blockSignals(False)
        self.update()
