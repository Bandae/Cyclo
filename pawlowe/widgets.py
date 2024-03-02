from PySide2.QtCore import Signal
from PySide2.QtWidgets import QFrame, QGridLayout, QComboBox
from common_widgets import DoubleSpinBox, QLabelD


class ResultsFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QGridLayout()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        data_label_names = ["F_max", "p_max", "N_Ck-ri"]
        self.data_labels = { key: QLabelD(style=False) for key in data_label_names}
        self.pressure_correct_label = QLabelD("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")

        fmax_label = QLabelD("F<sub>max</sub>", style=False)
        layout.addWidget(fmax_label, 0, 0, 1, 2)
        layout.addWidget(self.data_labels["F_max"], 0, 2)
        pmax_label = QLabelD("p<sub>max</sub>", style=False)
        layout.addWidget(pmax_label, 1, 0, 1, 2)
        layout.addWidget(self.data_labels["p_max"], 1, 2)
        layout.addWidget(self.pressure_correct_label, 2, 0, 1, 3)
        ncmr_label = QLabelD("N<sub>Ck-ri</sub>", style=False)
        layout.addWidget(ncmr_label, 3, 0, 1, 2)
        layout.addWidget(self.data_labels["N_Ck-ri"], 3, 2)

        self.setLayout(layout)
    
    def update(self, new_data, p_dop):
        data_units = [" N", " MPa", " W"]
        for index, (key, new_value) in enumerate(new_data.items()):
            self.data_labels[key].setText(str(new_value) + data_units[index])
        if new_data["p_max"] < p_dop:
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> spełniony.")
        else:
            self.pressure_correct_label.setText("Warunek p<sub>max</sub> &lt; p<sub>dop</sub> nie jest spełniony.")


class DaneMaterialowe(QFrame):
    changed = Signal()
    wheelMatChanged = Signal(dict, str)
    def __init__(self, nwej):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setMaximumHeight(400)

        self.materials = {
            "C30": {"nazwa": "C30", "type": "steel", "E": 210000, "v": 0.3, "p_dop_normalizowanie": 450, "p_dop_ulepszanie cieplne": 550, "p_dop_hartowanie": 1000},
            "C45": {"nazwa": "C45", "type": "steel", "E": 210000, "v": 0.3, "Re": 710, "p_dop_normalizowanie": 550, "p_dop_ulepszanie cieplne": 700, "p_dop_hartowanie": 1300, "tempered": True},
            "C55": {"nazwa": "C55", "type": "steel", "E": 210000, "v": 0.3, "Re": 810, "p_dop_normalizowanie": 600, "p_dop_ulepszanie cieplne": 900, "p_dop_hartowanie": 1500, "tempered": True},
            "50G": {"nazwa": "50G", "type": "steel", "E": 210000, "v": 0.3, "p_dop_ulepszanie cieplne": 900, "p_dop_hartowanie": 1450},
            "40H": {"nazwa": "40H", "type": "steel", "E": 210000, "v": 0.3, "p_dop_ulepszanie cieplne": 1000, "p_dop_hartowanie": 1550},
            "40HN": {"nazwa": "40HN", "type": "steel", "E": 210000, "v": 0.3, "p_dop_ulepszanie cieplne": 1000, "p_dop_hartowanie": 1600},

            "EN-GJL 200": {"nazwa": "EN-GJL 200", "type": "cast iron", "E": 98000, "v": 0.25, "p_dop_normalizowanie": 400},
            "EN-GJL 300": {"nazwa": "EN-GJL 300", "type": "cast iron", "E": 98000, "v": 0.25, "p_dop_normalizowanie": 500},
            "EN-GJL 400": {"nazwa": "EN-GJL 400", "type": "cast iron", "E": 98000, "v": 0.25, "p_dop_normalizowanie": 600},
            "Zs 50007": {"nazwa": "Zs 50007", "type": "cast iron", "E": 98000, "v": 0.25, "p_dop_normalizowanie": 550, "p_dop_ulepszanie cieplne": 800, "p_dop_hartowanie": 900},
            "Zs 70002": {"nazwa": "Zs 70002", "type": "cast iron", "E": 98000, "v": 0.25, "p_dop_normalizowanie": 600, "p_dop_ulepszanie cieplne": 1000, "p_dop_hartowanie": 1100},
            "Zs 90002": {"nazwa": "Zs 90002", "type": "cast iron", "E": 98000, "v": 0.25, "p_dop_normalizowanie": 750, "p_dop_ulepszanie cieplne": 1100, "p_dop_hartowanie": 1300},
        }
        self.current_mats = {"wheel": self.materials["C30"], "roller": self.materials["C30"]}
        self.other_data = {"b_wheel": 17, "f_kr": 0.00001, "f_ro": 0.00001}

        self.mat_inputs = {"wheel_mat": QComboBox(), "roller_mat": QComboBox(), "wheel_treat": QComboBox(), "roller_treat": QComboBox()}
        self.mat_inputs["wheel_mat"].addItems([mat["nazwa"] for mat in self.materials.values()])
        self.mat_inputs["roller_mat"].addItems([mat["nazwa"] for mat in self.materials.values() if mat["type"] == "steel"])
        
        self.mat_inputs["wheel_treat"].addItems(["normalizowanie", "ulepszanie cieplne", "hartowanie"])
        self.mat_inputs["roller_treat"].addItems(["normalizowanie", "ulepszanie cieplne", "hartowanie"])
        data_label_names = ["wh_E", "wh_v", "roll_E", "roll_v"]
        self.data_labels = { key: QLabelD(style=False) for key in data_label_names}

        self.data_inputs = {
            "b_wheel": DoubleSpinBox(self.other_data["b_wheel"], 10, 100, 2),
            "f_kr": DoubleSpinBox(self.other_data["f_kr"], 0.00001, 0.0001, 0.00001, 5),
            "f_ro": DoubleSpinBox(self.other_data["f_ro"], 0.00001, 0.0001, 0.00001, 5),
        }
        self.p_dop_label = QLabelD(style=False)
        self.n_out_label = QLabelD(nwej, style=False)
        for widget in self.data_inputs.values():
            widget.valueChanged.connect(self.update)
        self.mat_inputs["wheel_mat"].currentIndexChanged.connect(lambda: self.update(sendSignal=True))
        self.mat_inputs["roller_mat"].currentIndexChanged.connect(self.update)
        self.mat_inputs["wheel_treat"].currentIndexChanged.connect(lambda: self.updateTreat(sendSignal=True))
        self.mat_inputs["roller_treat"].currentIndexChanged.connect(self.updateTreat)

        self.setupLayout()
        self.update()

    def getAllowedPressure(self) -> int:
        wheel_treat = self.mat_inputs["wheel_treat"].currentText()
        roller_treat = self.mat_inputs["roller_treat"].currentText()
        wheel_p_dop = self.current_mats["wheel"]["p_dop_" + wheel_treat]
        roller_p_dop = self.current_mats["roller"]["p_dop_" + roller_treat]

        return min(wheel_p_dop, roller_p_dop)

    def setupLayout(self):
        layout = QGridLayout()
        layout.addWidget(QLabelD("DANE MATERIAŁOWE :", style=False), 0, 0, 1, 6)
        layout.addWidget(QLabelD("Koło", style=False), 1, 0, 1, 2)
        layout.addWidget(self.mat_inputs["wheel_mat"], 1, 2, 1, 2)
        layout.addWidget(self.mat_inputs["wheel_treat"], 1, 4, 1, 2)
        layout.addWidget(self.data_labels["wh_E"], 2, 0, 1, 3)
        layout.addWidget(self.data_labels["wh_v"], 2, 3, 1, 3)

        layout.addWidget(QLabelD("Rolka", style=False), 3, 0, 1, 2)
        layout.addWidget(self.mat_inputs["roller_mat"], 3, 2, 1, 2)
        layout.addWidget(self.mat_inputs["roller_treat"], 3, 4, 1, 2)
        layout.addWidget(self.data_labels["roll_E"], 4, 0, 1, 3)
        layout.addWidget(self.data_labels["roll_v"], 4, 3, 1, 3)

        layout.addWidget(QLabelD("Dopuszczalny nacisk między kołem a rolką", style=False), 5, 0, 1, 4)
        layout.addWidget(self.p_dop_label, 5, 4, 1, 2)

        layout.addWidget(QLabelD("Szerokość koła:", style=False), 6, 0, 1, 3)
        layout.addWidget(self.data_inputs["b_wheel"], 6, 3, 1, 2)

        layout.addWidget(QLabelD("DANE KINEMATYCZNE : ", style=False), 7, 0, 1, 5)
        layout.addWidget(QLabelD("Prędkość obrotowa wyj :", style=False), 8, 0, 1, 3)
        layout.addWidget(self.n_out_label, 8, 3, 1, 2)
        layout.addWidget(QLabelD("Współczynnik tarcia koło - rolka:", style=False), 9, 0, 1, 3)
        layout.addWidget(self.data_inputs["f_kr"], 9, 3, 1, 2)
        layout.addWidget(QLabelD("Współczynnik tarcia rolka - obudowa:", style=False), 10, 0, 1, 3)
        layout.addWidget(self.data_inputs["f_ro"], 10, 3, 1, 2)

        self.setLayout(layout)

    def update(self, sendSignal=False):
        wh_mat = self.materials[self.mat_inputs["wheel_mat"].currentText()]
        roll_mat = self.materials[self.mat_inputs["roller_mat"].currentText()]
        self.current_mats["wheel"] = wh_mat
        self.current_mats["roller"] = roll_mat

        self.mat_inputs["wheel_treat"].blockSignals(True)
        self.mat_inputs["roller_treat"].blockSignals(True)
        wheel_treat = self.mat_inputs["wheel_treat"].currentText()
        roller_treat = self.mat_inputs["roller_treat"].currentText()
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
        # TODO:
            # skoro dodanie przedmiotów powoduje sygnał indexChanged, to odpala sie znowu update, znowu dodane
            # dodanie treat powoduje nieskończona pętla. WIęc blokuje sygnały chwilowo. Może jest lepsza opcja.
        # chociaz jak wywalilem treat sygnał gdzie indziej to może nie przeszkadza.

        for key in self.other_data:
            self.other_data[key] = self.data_inputs[key].value()
        
        p_dop = self.getAllowedPressure()
        self.p_dop_label.setText(str(p_dop) + " MPa")
        self.data_labels["wh_E"].setText("E: " + str(wh_mat["E"]))
        self.data_labels["wh_v"].setText("v: " + str(wh_mat["v"]))
        self.data_labels["roll_E"].setText("E: " + str(roll_mat["E"]))
        self.data_labels["roll_v"].setText("v: " + str(roll_mat["v"]))

        if sendSignal:
            self.wheelMatChanged.emit(self.materials[self.mat_inputs["wheel_mat"].currentText()], self.mat_inputs["wheel_treat"].currentText())
        self.changed.emit()

    def updateTreat(self, sendSignal=False):
        p_dop = self.getAllowedPressure()
        self.p_dop_label.setText(str(p_dop) + " MPa")

        if sendSignal:
            self.wheelMatChanged.emit(self.materials[self.mat_inputs["wheel_mat"].currentText()], self.mat_inputs["wheel_treat"].currentText())
        self.changed.emit()

    def getData(self):
        copy = self.current_mats.copy()
        copy.update(self.other_data.copy())
        copy.update({
            "wheel_treat": self.mat_inputs["wheel_treat"].currentText(),
            "roller_treat": self.mat_inputs["roller_treat"].currentText(),
            "p_dop": self.getAllowedPressure(),
        })
        return copy

    def copyDataToInputs(self, new_input_data):
        for key in self.mat_inputs:
            self.mat_inputs[key].setCurrentText(new_input_data[key]["nazwa"])

        for key in self.other_data:
            self.data_inputs[key].setValue(new_input_data[key])
