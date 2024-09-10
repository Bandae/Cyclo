from typing import Dict, Optional, Tuple, Union
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton
from PySide2.QtCore import Signal

from .widgets import DaneMaterialowe, ResultsFrame
from ...model.gear_calc import calculate_gear, get_lam_min, get_ro_min, gear_error_check

from tabs.common.widgets.abstract_tab import AbstractTab
from common.common_widgets import IntSpinBox, DoubleSpinBox, QLabelD

class EntryDataTab(QWidget):
    chartDataUpdated = Signal(dict)
    animDataUpdated = Signal(dict)
    errorsUpdated = Signal(dict)
    shouldSendData = Signal()

    def __init__(self, parent: AbstractTab) -> None:
        super().__init__(parent)
        self.dane_all = {
            "z" : 24,       "ro" : 5.8,
            "lam" : 0.625,  "g" : 11,
            "Ra1" : 0,      "Rf1": 0,
            "Rw1": 0,       "Ra2": 0,
            "Rf2": 0,       "Rw2": 0,
            "Rb" : 0,       "Rb2": 0,
            "Rg" : 0,       "sr": 0,
            "e" : 0,        "h" : 0,
            "K" : 2,        "nwyj" : 21,
        }
        self.tolerances = None
        self.outside_data = {
            "i": 24,
            "M_wyj": 500,
            "n_wej": 500,
        }

        self.dane_materialowe = DaneMaterialowe(self.dane_all["nwyj"])
        self.results_frame = ResultsFrame(self)

        self.label_z = QLabelD(str(self.dane_all["z"]))
        self.spin_ro = DoubleSpinBox(self.dane_all["ro"],1,8,0.05)
        self.spin_lam = DoubleSpinBox(self.dane_all["lam"],0.5,0.99,0.01, 3)
        self.spin_g = DoubleSpinBox(self.dane_all["g"],3,14,0.02)
        self.spin_l_k = IntSpinBox(self.dane_all["K"], 1, 2, 1)

        self.accept_button = QPushButton("Oblicz")
        self.accept_button.clicked.connect(lambda: self.inputsModified(True))
        self.accept_button.clicked.connect(lambda: self.accept_button.setEnabled(False))

        self.dane_materialowe.changed.connect(lambda: self.accept_button.setEnabled(True))
        self.spin_ro.valueChanged.connect(lambda: self.inputsModified(False))
        self.spin_lam.valueChanged.connect(lambda: self.inputsModified(False))
        self.spin_g.valueChanged.connect(lambda: self.inputsModified(False))
        self.spin_l_k.valueChanged.connect(lambda: self.inputsModified(False))

        self.data_labels = {
            "sr": QLabelD(str(self.dane_all["sr"]) + " mm"),
            "Ra1": QLabelD(str(self.dane_all["Ra1"]) + " mm"),
            "Rf1": QLabelD(str(self.dane_all["Rf1"]) + " mm"),
            "Rw1": QLabelD(str(self.dane_all["Rw1"]) + " mm"),
            "Ra2": QLabelD(str(self.dane_all["Ra2"]) + " mm"),
            "Rf2": QLabelD(str(self.dane_all["Rf2"]) + " mm"),
            "Rw2": QLabelD(str(self.dane_all["Rw2"]) + " mm"),
            # "Rb": QLabelD(str(self.dane_all["Rb"]) + " mm"),
            "Rg": QLabelD(str(self.dane_all["Rg"]) + " mm"),
            # "g": QLabelD(str(self.dane_all["g"]) + " mm"),
            "e": QLabelD(str(self.dane_all["e"]) + " mm"),
            "h": QLabelD(str(self.dane_all["h"]) + " mm"),
        }

        self.label_descriptions = {
            "sr": "Średnica zewnętrzna przekładni",
            "Ra1": "Promień koła wierzchołkowego",
            "Rf1": "Promień koła stóp",
            "Rw1": "Promień koła tocznego",
            "Ra2": "Promień koła wierzchołkowego",
            "Rf2": "Promień koła stóp",
            "Rw2": "Promień koła tocznego",
            "Rg": "Promień rozmieszczenia rolek",
            "e": "Mimośród",
            "h": "Wysokość zęba",
        }

        layout = QGridLayout()
        self.setupSmallLayout(layout)
        self.setLayout(layout)
        self.refillData()
        self.recalculate()
        self.accept_button.setEnabled(False)
    
    def setupLayout(self, layout: QGridLayout) -> None:
        layout.addWidget(QLabelD("DANE WEJSCIOWE:"), 0, 0, 1, 3)
        layout.addWidget(QLabelD("Liczba Kół - K"), 1, 0, 1, 2)
        layout.addWidget(self.spin_l_k, 1, 2, 1, 1)
        layout.addWidget(QLabelD("Liczba Zębów - z"), 2, 0, 1, 2)
        layout.addWidget(self.label_z, 2, 2, 1, 1)
        layout.addWidget(QLabelD("Promień - ρ [mm]"), 3, 0, 1, 2)
        layout.addWidget(self.spin_ro, 3, 2, 1, 1)
        layout.addWidget(QLabelD("Wsp. wysokości zęba - λ"), 4, 0, 1, 2)
        layout.addWidget(self.spin_lam, 4, 2, 1, 1)
        layout.addWidget(QLabelD("Promień rolek - g [mm]"), 5, 0, 1, 2)
        layout.addWidget(self.spin_g, 5, 2, 1, 1)
        
        label = QLabelD("sr")
        layout.addWidget(label, 7, 0, 1, 2)
        label.setToolTip(self.label_descriptions["sr"])
        layout.addWidget(self.data_labels["sr"], 7, 2, 1, 1)

        layout.addWidget(QLabelD("Obiegowe koło cykloidalne:"), 8, 0, 1, 3)
        for index, (text, qlabel) in enumerate(self.data_labels.items(), start=1):
            # rozdzielenie na dwie czesci, zeby podpisac co sie tyczy jakiego koła.
            if "1" in text:
                name_label = QLabelD(text)
                name_label.setToolTip(self.label_descriptions[text])
                layout.addWidget(name_label, 8+index, 0, 1, 2)
                layout.addWidget(qlabel, 8+index, 2, 1, 1)
        
        layout.addWidget(QLabelD("Koło współpracujące:"), 12, 0, 1, 3)
        roller_labels = {text: qlabel for text, qlabel in self.data_labels.items() if text in ("Ra2", "Rf2", "Rw2", "Rg", "e", "h")}
        for index, (text, qlabel) in enumerate(roller_labels.items(), start=1):
            name_label = QLabelD(text)
            name_label.setToolTip(self.label_descriptions[text])
            layout.addWidget(name_label, 12+index, 0, 1, 2)
            layout.addWidget(qlabel, 12+index, 2, 1, 1)

        layout.addWidget(self.dane_materialowe, 0, 3, 10, 6)
        layout.addWidget(self.accept_button, 10, 5, 1, 2)
        layout.addWidget(self.results_frame, 11, 5, 7, 4)
    
    def setupSmallLayout(self, layout: QGridLayout) -> None:
        layout.addWidget(QLabelD("DANE WEJSCIOWE:"), 0, 0, 1, 6)
        layout.addWidget(QLabelD("Liczba Kół - K"), 1, 0, 1, 4)
        layout.addWidget(self.spin_l_k, 1, 4, 1, 2)
        layout.addWidget(QLabelD("Liczba Zębów - z"), 3, 0, 1, 4)
        layout.addWidget(self.label_z, 3, 4, 1, 2)
        layout.addWidget(QLabelD("Promień - ρ [mm]"), 4, 0, 1, 4)
        layout.addWidget(self.spin_ro, 4, 4, 1, 2)
        layout.addWidget(QLabelD("Wsp. wysokości zęba - λ"), 5, 0, 1, 4)
        layout.addWidget(self.spin_lam, 5, 4, 1, 2)
        layout.addWidget(QLabelD("Promień rolek - g [mm]"), 6, 0, 1, 4)
        layout.addWidget(self.spin_g, 6, 4, 1, 2)

        layout.addWidget(self.dane_materialowe, 7, 0, 10, 6)
        layout.addWidget(self.accept_button, 17, 0, 1, 6)

        layout.addWidget(QLabelD(self.label_descriptions["sr"]), 18, 0, 1, 4)
        layout.addWidget(self.data_labels["sr"], 18, 4, 1, 2)
        layout.addWidget(QLabelD("Obiegowe koło cykloidalne:"), 19, 0, 1, 6)
        for index, (text, qlabel) in enumerate(self.data_labels.items(), start=1):
            # rozdzielenie na dwie czesci, zeby podpisac co sie tyczy jakiego koła.
            if "1" in text:
                layout.addWidget(QLabelD(self.label_descriptions[text]), 19+index, 0, 1, 4)
                layout.addWidget(qlabel, 19+index, 4, 1, 2)
        
        layout.addWidget(QLabelD("Koło współpracujące:"), 24, 0, 1, 6)
        roller_labels = {text: qlabel for text, qlabel in self.data_labels.items() if text in ("Ra2", "Rf2", "Rw2", "Rg", "e", "h")}
        for index, (text, qlabel) in enumerate(roller_labels.items(), start=1):
            layout.addWidget(QLabelD(self.label_descriptions[text]), 24+index, 0, 1, 4)
            layout.addWidget(qlabel, 24+index, 4, 1, 2)

        layout.addWidget(self.results_frame, 31, 0, 6, 6)

    def refillData(self) -> None:
        z=self.dane_all["z"]
        ro=self.dane_all["ro"]
        lam=self.dane_all["lam"]
        g=self.dane_all["g"]
        self.dane_all["Ra1"] = round(ro*(z+1+lam)-g, 3)
        self.dane_all["Rf1"] = round(ro*(z+1-lam)-g, 3)
        self.dane_all["Rw1"] = round(ro*lam*z, 3)
        self.dane_all["Ra2"] = round(ro*(z+1)-g, 3)
        self.dane_all["Rf2"] = self.dane_all["Ra1"]
        self.dane_all["Rw2"] = round(ro*lam*(z+1), 3)
        self.dane_all["Rb"] = round(ro*z, 3)
        self.dane_all["Rg"] = round(ro*(z+1), 3)
        self.dane_all["e"] = round(ro*lam, 3)
        self.dane_all["Rb2"] = self.dane_all["e"]+g+self.dane_all["Rf1"]
        self.dane_all["h"] = 2*self.dane_all["e"]
        self.dane_all["sr"] = round((2*g)+(2*self.dane_all["Rb2"]), 2)

    def inputsModified(self, calculate: bool) -> None:
        self.dane_all["ro"] = self.spin_ro.value()
        self.dane_all["lam"] = self.spin_lam.value()
        self.dane_all["g"] = self.spin_g.value()
        self.dane_all["K"] = self.spin_l_k.value()

        ro_min = get_ro_min(self.dane_all["z"], self.dane_all["lam"], self.dane_all["g"])
        self.spin_ro.setMinimum(ro_min + 0.01)

        self.refillData()

        if calculate:
            self.recalculate()
            self.accept_button.setEnabled(False)
        else:
            errors = self.sendAnimationData()
            self.errorsUpdated.emit(errors)
            self.shouldSendData.emit()
            self.accept_button.setEnabled(True)
    
    def baseDataChanged(self, new_data: Dict[str, Dict[str, int]], calculate: bool) -> None:
        if new_data is None:
            return
        for key in new_data:
            if self.outside_data.get(key) is not None:
                self.outside_data[key] = new_data[key]
        
        self.dane_all["z"] = self.outside_data["i"]
        self.label_z.setText(str(self.dane_all["z"]))

        h_min = get_lam_min(self.dane_all["z"])
        self.spin_lam.setMinimum(h_min + 0.001)

        ro_min = get_ro_min(self.dane_all["z"], self.dane_all["lam"], self.dane_all["g"])
        self.spin_ro.setMinimum(ro_min + 0.01)

        self.refillData()
        if calculate:
            self.recalculate()
        else:
            errors = self.sendAnimationData()
            self.errorsUpdated.emit(errors)
            self.shouldSendData.emit()
            self.accept_button.setEnabled(True)

    def sendAnimationData(self) -> None:
        errors = gear_error_check(self.dane_all["z"], self.dane_all["lam"], self.dane_all["g"], self.dane_all["e"], self.dane_all["Rg"], self.dane_all["ro"])
        if errors:
            # nie rysuje jeśli są błędy inne niż za duże p.
            self.animDataUpdated.emit({"GearTab": False})
        else:
            self.animDataUpdated.emit({"GearTab": self.dane_all.copy()})
        
        return errors

    def recalculate(self) -> None:
        material_data = self.dane_materialowe.getData()
        results = calculate_gear(self.dane_all, material_data, self.outside_data, self.tolerances)

        self.chartDataUpdated.emit({
            "sily": results["sily"],
            "naciski": results["naciski"],
            "straty": results["straty"],
            "luzy": results["luzy"],
        })

        self.results_frame.update(results, material_data["p_dop"])
        self.dane_all["nwyj"] = round(self.outside_data["n_wej"] / self.dane_all["z"], 2)
        self.dane_materialowe.n_out_label.setText(str(self.dane_all["nwyj"]) + " obr/min")

        errors = self.sendAnimationData()
        if results["p_max"] > material_data["p_dop"]:
            self.errorsUpdated.emit({"naciski przekroczone": True})
        else:
            self.errorsUpdated.emit(errors)
        
        for text, qlabel in self.data_labels.items():
            qlabel.setText(str(round(self.dane_all[text], 2)) + " mm")

        self.shouldSendData.emit()

    def copyDataToInputs(self, new_input_data: Dict[str, Union[int, float]]) -> None:
        self.spin_ro.setValue(new_input_data["ro"])
        self.spin_lam.setValue(new_input_data["lam"])
        self.spin_g.setValue(new_input_data["g"])
        self.spin_l_k.setValue(new_input_data["K"])

        self.inputsModified(True)
        self.dane_all = new_input_data
    
    def toleranceUpdate(self, tol_data: Optional[Dict[str, Union[float, Tuple[float, float]]]]) -> None:
        self.tolerances = tol_data
        self.recalculate()