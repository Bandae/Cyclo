from functools import partial
from typing import Dict, Optional, Tuple, Union
import math
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QHBoxLayout, QStackedLayout
from modules.common.abstract_tab import AbstractTab
from common.common_widgets import IntSpinBox, DoubleSpinBox, QLabelD, ResponsiveContainer
from modules.common.widgets.tolerance_widgets import ToleranceEdit
from modules.common.widgets.charts import ResultsTab
from .widgets import DaneMaterialowe, ResultsFrame
from .calculations import calculate_gear, get_lam_min, get_ro_min, gear_error_check
from common.utils import open_pdf
#TODO: nie podoba mi się obliczanie p_max, jako po prostu największego nacisku z wszystkich. U wiktora jest p_max wiekszy niz na sworzniu czasem, bo sworzen zmienia p jak sie obraca.


class DataEdit(QWidget):
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

        results.update({"p_dop": material_data["p_dop"]})
        self.results_frame.update(results)
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


class GearTab(AbstractTab):
    wheel_mat_updated = Signal(dict)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        stacklayout = QStackedLayout()
        layout.addLayout(button_layout)
        layout.addLayout(stacklayout)
        self.data = DataEdit(self)
        self.wykresy = ResultsTab(self, "Numer Rolki [n]", {
            "sily": {"repr_name": "Siły", "chart_title": "Wykres Sił w rolkach", "y_axis_title": "Wartość Siły [N]"},
            "naciski": {"repr_name": "Naprężenia", "chart_title": "Wykres Naprężeń w rolkach", "y_axis_title": "Wartość Nacisku [MPa]"},
            "straty": {"repr_name": "Straty Mocy", "chart_title": "Wykres Strat mocy w rolkach", "y_axis_title": "Wartość Straty [W]"},
            "luzy": {"repr_name": "Luz Międzyzębny", "chart_title": "Wykres luzów międzyzębnych w rolkach", "y_axis_title": "Wartość Luzu [mm]"},
        })

        self.tolerance_edit = ToleranceEdit(self, (
            ("T_ze", "T<sub>ze</sub>", "Tolerancja wykonanania zarysu koła obiegowego"),
            ("T_Rg", "T<sub>Rg</sub>", "Tolerancja wykonania rolki"),
            ("T_fi_Ri", "T<sub>\u03c6Ri</sub>", "Tolerancja wykonania promienia rozmieszczenia rolek w obudowie"),
            ("T_Rr", "T<sub>Rr</sub>", "Tolerancja kątowego rozmieszczenia rolek w obudowie"),
            ("T_e", "T<sub>e</sub>", "Tolerancja wykonania mimośrodu"),
        ))
        self.data.shouldSendData.connect(self.sendData)
        self.data.chartDataUpdated.connect(self.wykresy.updateResults)
        self.tolerance_edit.toleranceDataUpdated.connect(self.data.toleranceUpdate)

        help_pdf_button = QPushButton("Pomoc")
        button_layout.addWidget(help_pdf_button)
        help_pdf_button.clicked.connect(lambda: open_pdf("resources//help_docs//zazebienie-help-1.pdf"))

        scrollable_tab = ResponsiveContainer(self, self.data, self.data.setupSmallLayout, self.data.setupLayout, 480, 1300)
        tab_titles = ["Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        stacked_widgets = [scrollable_tab, self.wykresy, self.tolerance_edit]

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button)
            stacklayout.addWidget(widget)
            button.pressed.connect(partial(stacklayout.setCurrentIndex, index))
        
        self.setLayout(layout)

    def sendData(self) -> None:
        material_data = self.data.dane_materialowe.getData()
        
        self.dataChanged.emit({"GearTab": {
            "R_w1": self.data.dane_all["Rw1"],
            "R_f1": self.data.dane_all["Rf1"],
            "Fwzx": self.data.results_frame.data["F_wzx"],
            "Fwzy": self.data.results_frame.data["F_wzy"],
            "e": self.data.dane_all["e"],
            "K": self.data.dane_all["K"],
            "B": material_data["b_wheel"],
        }})
    
    def receiveData(self, new_data) -> None:
        base_data = new_data.get("base")
        if base_data is None:
            return
        calculate = not self.data.accept_button.isEnabled()
        self.data.baseDataChanged(base_data, calculate)
    
    def saveData(self):
        self.data.inputsModified(True)
        return {
            "dane_all": self.data.dane_all,
            "material_data": self.data.dane_materialowe.getData(),
        }

    def loadData(self, new_data) -> None:
        if new_data is None:
            return
        self.data.copyDataToInputs(new_data["dane_all"])
        self.data.dane_materialowe.copyDataToInputs(new_data["material_data"])
        self.data.dane_all = new_data["dane_all"]
    
    def reportData(self) -> str:
        def indent_point(point_text, bullet, bold, sa=100):
            bullet_code = "\\bullet" if bullet else ""
            bold_code = "\\b" if bold else ""
            return f"{{\\pard\\sa{str(sa)}\\fi-300\\li600{bullet_code}{bold_code}\\tab {point_text} \\par}}"

        materials = self.data.dane_materialowe.getData()
        results = calculate_gear(self.data.dane_all, self.data.dane_materialowe.getData(), self.data.outside_data)

        text = "{\\pard\\b Zazębienie \\line\\par}"
        text += indent_point("Materiały", True, True)
        text += "{\\pard\\sa100 - koło podstawowe: \\par}"
        text += indent_point(f"Materiał: {materials['wheel']['nazwa']}", False, False)
        text += indent_point(f"Moduł Younga: E = {materials['wheel']['E']} [MPa]", False, False)
        text += indent_point(f"Liczba Poissona: v = {materials['wheel']['v']}", False, False)
        text += "{\\pard\\sa100 - koło współpracujące (rolki): \\par}"
        text += indent_point(f"Materiał: {materials['roller']['nazwa']}", False, False)
        text += indent_point(f"Moduł Younga: E = {materials['roller']['E']} [MPa]", False, False)
        text += indent_point(f"Liczba Poissona: v = {materials['roller']['v']}", False, False)

        text += f"{{\\pard\\sa100 Nacisk dopuszczalny (dla pary materiałów): p{{\sub dop}} = {materials['p_dop']} [MPa]\\par}}"
        text += f"{{\\pard\\sa100 Współczynnik tarcia tocznego pomiędzy zarysem koła a rolkami: f{{\sub k-r}} = {materials['f_kr']:.5f} [m]\\par}}"
        text += f"{{\\pard\\sa500 Współczynnik tarcia tocznego pomiędzy rolkami a obudową: f{{\sub r-o}} = {materials['f_ro']:.5f} [m]\\par}}"

        text += "{\\pard\\sa200\\b Obliczenia: \\par}"
        text += indent_point("Geometria kół:", True, True)
        text += "{\\pard\\sa100 - koło podstawowe: \\par}"
        text += indent_point(f"Liczba zębów: z{{\sub 1}} = {self.data.dane_all['z']}", False, False)
        text += indent_point(f"Promień (średnica) koła wierzchołkowego: r{{\sub a1}} = {self.data.dane_all['Ra1']} ({self.data.dane_all['Ra1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła stóp: r{{\sub f1}} = {self.data.dane_all['Rf1']} ({self.data.dane_all['Rf1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła tocznego: r{{\sub w1}} = {self.data.dane_all['Rw1']} ({self.data.dane_all['Rw1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła zasadniczego: r{{\sub b1}} = {self.data.dane_all['Rb']} ({self.data.dane_all['Rb'] * 2}) [mm]", False, False)
        text += indent_point(f"Wysokość zęba: h = {self.data.dane_all['h']} [mm]", False, False)
        text += indent_point(f"Szerokość koła: B = {materials['b_wheel']} [mm]", False, False)

        text += "{\\pard\\sa100 - koło współpracujące: \\par}"
        text += indent_point(f"Liczba zębów (rolek): z{{\sub 2}} = {self.data.dane_all['z'] + 1}", False, False)
        text += indent_point(f"Promień (średnica) rolki: r{{\sub r}} = {self.data.dane_all['g']} ({self.data.dane_all['g'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) rozmieszczenia rolek: r{{\sub b2}} = {self.data.dane_all['Rb2']} ({self.data.dane_all['Rb2'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła tocznego: r{{\sub w2}} = {self.data.dane_all['Rw2']} ({self.data.dane_all['Rw2'] * 2}) [mm]", False, False)
        text += indent_point(f"Mimośród: e = {self.data.dane_all['e']} [mm]", False, False, 500)

        text += indent_point("Siły międzyzębne:", True, True)
        text += indent_point(f"Maksymalna siła międzyzębna: F{{\sub max}} = {results['F_max']} [N]", False, False)
        text += indent_point(f"Całkowita siła międzyzębna dla osi 0X: F{{\sub wzx}} = {results['F_wzx']} [N]", False, False)
        text += indent_point(f"Całkowita siła międzyzębna dla osi 0Y: F{{\sub wzy}} = {results['F_wzy']} [N]", False, False)
        text += indent_point(f"Całkowita wypadkowa siła międzyzębna: F{{\sub wz}} = {results['F_wz']} [N]", False, False, 500)
        text += indent_point("Naciski międzyzębne:", True, True)
        text += indent_point(f"Maksymalne naciski międzyzębne: p{{\sub max}} = {results['p_max']} [MPa]", False, False)
        text += f"{{\\pard\\sa500\\qc Warunek p{{\sub max}} = {results['p_max']} [MPa] < p{{\sub dop}} = {materials['p_dop']} [MPa] został spełniony. \\par}}"

        text += indent_point("Moc tracona:", True, True)
        text += indent_point(f"Prędkość kątowa wałka czynnego: \\uc1\\u969*{{\sub wej}} = {round(math.pi * self.data.outside_data['n_wej'] / 30, 2)} [rad/s]", False, False)
        text += indent_point(f"Całkowita strata mocy: N{{\sub Ck-r}} = {round(sum(results['straty'][0]), 3)} [W]", False, False)
        text += indent_point(f"Prędkość obrotowa wałka biernego: n{{\sub wyj}} = {self.data.dane_all['nwyj']} [obr/min]", False, False)
        text += indent_point(f"Prędkość kątowa wałka biernego: \\uc1\\u969*{{\sub wyj}} = {round(math.pi * self.data.dane_all['nwyj'] / 30, 2)} [rad/s]", False, False, 500)

        a = "{\\trowd\\trleft3200"
        b = "{\\trowd\\trleft4000"
        borders = "\\clbrdrt\\brdrw15\\brdrs\\clbrdrl\\brdrw15\\brdrs\\clbrdrb\\brdrw15\\brdrs\\clbrdrr\\brdrw15\\brdrs\\clvertalc"
        start = "\\pard\\intbl\\qc "
        end = "\\cell"
        endrow = "\\row}"

        text += b + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + "F{\sub i}" + end + start + "p{\sub i}" + end + start + "N{\sub k-ri}" + end + endrow
        text += a + borders + "\\cellx4000" + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + "Nr rolki" + end + start + "[N]" + end + start + "[MPa]" + end + start + "[W]" + end + endrow
        for index, row in enumerate(zip(results["sily"][0], results["naciski"][0], results["straty"][0]), 1):
            text += a + borders + "\\cellx4000" + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + str(index) + end + start + "{:.1f}".format(row[0]) + end + start + "{:.2f}".format(row[1]) + end + start + "{:.3f}".format(row[2]) + end + endrow

        text += "\\line"
        return text
