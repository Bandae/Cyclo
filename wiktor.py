from functools import partial
from math import pi
from typing import Dict, Union

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QStackedLayout, QCheckBox

from abstract_tab import AbstractTab
from common_widgets import DoubleSpinBox, QLabelD, IntSpinBox, ResponsiveContainer
from utils import open_pdf
from Mech_wyj_tuleje.popups import SupportWin
from Mech_wyj_tuleje.tuleje_obl import obliczenia_mech_wyjsciowy
from Mech_wyj_tuleje.utils import sprawdz_przecinanie_otworow
from Mech_wyj_tuleje.tolerances import ToleranceEdit
from Mech_wyj_tuleje.widgets import ResultsFrame, MaterialsFrame
from Mech_wyj_tuleje.wykresy import ResultsTab
#TODO: mam przesunięte do tyłu w poziomie punkty wykresów. Pawel też.
# moze jakos usuwac dane z wykresow jak sa bledy?
# po trzy razy wysylam dane w niektorych sytuacjach, np jak sie zaznaczy zeby uzywac tego. Może to jest pętla.
#TODO: moze zrobic w animacji painter.save() i .restore() zamiast obrotów -self.kat_dorotacji
#TODO: ukrywanie label e2 teraz jak jest QSCrollArea nie dziala, bo to sie dzieje na zewnatrz, pokazanie wszystkich widzetow

class DataEdit(QWidget):
    chartDataUpdated = Signal(dict)
    chartDataMove = Signal(float)
    animDataUpdated = Signal(dict)
    errorsUpdated = Signal(dict)
    shouldSendData = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.wheel_rotation_angle = 0
        self.module_enabled = False
        self.tol_data = {"tolerances": None}
        self.input_dane = {
            "M_k": 500,
            "n": 10,
            "R_wt": 80,
            "podparcie": "jednostronnie utwierdzony",
            "d_sw": 10,
            "d_tul": 14,
            "wsp_k": 1.2,
            "e1": 1,
            "e2": 1,
            "f_kt": 0.00005,
            "f_ts": 0.00005,
        }
        self.obliczone_dane = {
            "d_sw": 10,
            "d_tul": 14,
            "d_otw": 20,
            "F_max": 1200,
            "p_max": 200,
            "F_wmr": 1000,
            "r_mr": 80,
            "N_cmr": 10,
        }
        self.zew_dane = {
            "R_w1": 72,
            "R_f1": 107,
            "e": 3,
            "K": 2,
            "B": 20,
            "M_wyj": 500,
            "n_wej": 500,
        }

        self.input_widgets = {
            "n": IntSpinBox(self.input_dane["n"], 4, 28, 1),
            "R_wt": DoubleSpinBox(self.input_dane["R_wt"], 20, 300, 1, 1),
            "e1": DoubleSpinBox(self.input_dane["e1"], 0, 10, 0.05),
            "e2": DoubleSpinBox(self.input_dane["e2"], 0, 10, 0.05),
            "wsp_k": DoubleSpinBox(self.input_dane["wsp_k"], 1.2, 1.5, 0.05),
            "d_sw": DoubleSpinBox(self.input_dane["d_sw"], 5, 14, 0.1),
            "d_tul": DoubleSpinBox(self.input_dane["d_tul"], 5, 14, 0.1),
            "f_kt": DoubleSpinBox(self.input_dane["f_kt"], 0.00001, 0.0001, 0.00001, 5),
            "f_ts": DoubleSpinBox(self.input_dane["f_ts"], 0.00001, 0.0001, 0.00001, 5),
        }

        self.Rwk_label = QLabelD("")

        self.support_popup = SupportWin()
        self.support_popup.choiceMade.connect(self.closeChoiceWindow)
        self.ch_support_button = QPushButton(text="Wybierz sposób podparcia kół")
        self.ch_support_button.clicked.connect(self.support_popup.show)
        self.ch_var_label = QLabelD("jednostronnie utwierdzony")

        self.results_frame = ResultsFrame(self)
        self.material_frame = MaterialsFrame(self)

        self.label_e2 = QLabelD("Odstęp pomiędzy kołami")
        self.obl_srednice_labels = [QLabelD(style=False), QLabelD(style=False), QLabelD(style=False)]

        self.accept_button = QPushButton("Oblicz")
        self.accept_button.clicked.connect(self.inputsModified)
        self.accept_button.clicked.connect(lambda: self.accept_button.setEnabled(False))

        # wczesniej byly wszystkie ale jest przycisk oblicz
        for key in self.input_widgets:
            if key in ["d_sw", "d_tul", "wsp_k"]:
                self.input_widgets[key].valueChanged.connect(self.inputsModified)
            else:
                self.input_widgets[key].valueChanged.connect(lambda: self.accept_button.setEnabled(True))
        self.material_frame.updated.connect(lambda: self.accept_button.setEnabled(True))
        
        layout = QGridLayout()
        self.setupSmallLayout(layout)
        self.setLayout(layout)
        self.inputsModified()
    
    def setupLayout(self, layout: QGridLayout) -> None:
        # layout.setVerticalSpacing(10)
        n_label = QLabelD("Liczba sworzni [n]")
        layout.addWidget(n_label, 0, 0, 1, 2)
        layout.addWidget(self.input_widgets["n"], 0, 2, 1, 2)
        lab_Rwt = QLabelD("R<sub>wt</sub> [mm]")
        lab_Rwt.setToolTip("Promień rozmieszczenia sworzni")
        layout.addWidget(lab_Rwt, 1, 0)
        layout.addWidget(self.input_widgets["R_wt"], 1, 1)
        name_Rwk = QLabelD("R<sub>wk</sub>")
        name_Rwk.setToolTip("Promień rozmieszczenia otworów w kole cykloidalnym")
        layout.addWidget(name_Rwk, 1, 2)
        layout.addWidget(self.Rwk_label, 1, 3)
        layout.addWidget(self.material_frame, 0, 5, 6, 4)
        layout.addWidget(self.ch_support_button, 2, 0, 1, 2)
        layout.addWidget(self.ch_var_label, 2, 2, 1, 2)
        layout.addWidget(QLabelD("Odstęp pomiędzy kołem a tarczą"), 3, 0, 1, 3)
        layout.addWidget(self.input_widgets["e1"], 3, 3)
        layout.addWidget(self.label_e2, 4, 0, 1, 3)
        layout.addWidget(self.input_widgets["e2"], 4, 3)

        layout.addWidget(QLabelD("Współczynniki tarcia dla pary ciernej:", style=False), 6, 5, 1, 4)
        lab_f_kt = QLabelD("tuleja - koło cykloidalne")
        # lab_f_kt = QLabelD("f<sub>kt</sub>")
        # lab_f_kt.setToolTip("f kt - Współczynnik tarcia tocznego pomiędzy otworem w kole a tuleją")
        layout.addWidget(lab_f_kt, 7, 5, 1, 3)
        layout.addWidget(self.input_widgets["f_kt"], 7, 8)
        lab_f_ts = QLabelD("sworzeń - tuleja")
        # lab_f_ts = QLabelD("f<sub>ts</sub>")
        # lab_f_ts.setToolTip("f ts -Współczynnik tarcia tocznego pomiędzy tuleją a sworzniem")
        layout.addWidget(lab_f_ts, 8, 5, 1, 3)
        layout.addWidget(self.input_widgets["f_ts"], 8, 8)

        # spac = QSpacerItem(100, 100, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # layout.addItem(spac, 10, 0)
        # layout.addItem(spac, 0, 4)

        layout.addWidget(self.accept_button, 11, 3, 1, 3)
        self.accept_button.show()

        layout.addWidget(QLabelD("Obliczone średnice:"), 12, 0, 1, 4)
        layout.addWidget(QLabelD("sworznia - d<sub>s</sub>"), 13, 0)
        layout.addWidget(QLabelD("tuleji - d<sub>t</sub>"), 13, 1)
        
        layout.addWidget(self.obl_srednice_labels[0], 14, 0)
        layout.addWidget(self.obl_srednice_labels[1], 14, 1)
        lab_k = QLabelD("k")
        lab_k.setToolTip("Współczynnik grubości ścianki tuleji")
        layout.addWidget(lab_k, 15, 0)
        layout.addWidget(self.input_widgets["wsp_k"], 15, 1)
        layout.addWidget(QLabelD("Dobierz średnice [mm]:"), 16, 0, 1, 4)
        layout.addWidget(QLabelD("sworznia - d<sub>s</sub>"), 17, 0)
        layout.addWidget(QLabelD("tuleji - d<sub>t</sub>"), 17, 1)
        layout.addWidget(QLabelD("otworów - d<sub>otw</sub>"), 17, 2)
        layout.addWidget(self.input_widgets["d_sw"], 18, 0)
        layout.addWidget(self.input_widgets["d_tul"], 18, 1)
        layout.addWidget(self.obl_srednice_labels[2], 18, 2)

        layout.addWidget(self.results_frame, 12, 6, 6, 3)
        self.results_frame.show()

    def setupSmallLayout(self, layout: QGridLayout) -> None:
        n_label = QLabelD("Liczba sworzni [n]")
        layout.addWidget(n_label, 0, 0, 1, 6)
        layout.addWidget(self.input_widgets["n"], 0, 6, 1, 6)
        lab_Rwt = QLabelD("R<sub>wt</sub> [mm]")
        lab_Rwt.setToolTip("Promień rozmieszczenia sworzni")
        layout.addWidget(lab_Rwt, 1, 0, 1, 3)
        layout.addWidget(self.input_widgets["R_wt"], 1, 3, 1, 3)
        name_Rwk = QLabelD("R<sub>wk</sub>")
        name_Rwk.setToolTip("Promień rozmieszczenia otworów w kole cykloidalnym")
        layout.addWidget(name_Rwk, 1, 6, 1, 3)
        layout.addWidget(self.Rwk_label, 1, 9, 1, 3)

        layout.addWidget(self.ch_support_button, 2, 0, 1, 6)
        layout.addWidget(self.ch_var_label, 2, 6, 1, 6)
        layout.addWidget(QLabelD("Odstęp pomiędzy kołem a tarczą"), 3, 0, 1, 6)
        layout.addWidget(self.input_widgets["e1"], 3, 6, 1, 6)
        layout.addWidget(self.label_e2, 4, 0, 1, 6)
        layout.addWidget(self.input_widgets["e2"], 4, 6, 1, 6)

        layout.addWidget(self.material_frame, 5, 0, 8, 12)

        layout.addWidget(QLabelD("Współczynniki tarcia dla pary ciernej:", style=False), 13, 0, 1, 12)
        lab_f_kt = QLabelD("tuleja - koło cykloidalne")
        layout.addWidget(lab_f_kt, 14, 0, 1, 6)
        layout.addWidget(self.input_widgets["f_kt"], 14, 6, 1, 6)
        lab_f_ts = QLabelD("sworzeń - tuleja")
        layout.addWidget(lab_f_ts, 15, 0, 1, 6)
        layout.addWidget(self.input_widgets["f_ts"], 15, 6, 1, 6)

        layout.addWidget(self.accept_button, 16, 4, 1, 4)

        layout.addWidget(QLabelD("Obliczone średnice:"), 17, 0, 1, 12)
        layout.addWidget(QLabelD("sworznia - d<sub>s</sub>"), 18, 0, 1, 4)
        layout.addWidget(QLabelD("tuleji - d<sub>t</sub>"), 18, 4, 1, 4)
        
        layout.addWidget(self.obl_srednice_labels[0], 19, 0, 1, 4)
        layout.addWidget(self.obl_srednice_labels[1], 19, 4, 1, 4)
        lab_k = QLabelD("k")
        lab_k.setToolTip("Współczynnik grubości ścianki tuleji")
        layout.addWidget(lab_k, 20, 0, 1, 6)
        layout.addWidget(self.input_widgets["wsp_k"], 20, 6, 1, 6)
        layout.addWidget(QLabelD("Dobierz średnice [mm]:"), 21, 0, 1, 12)
        layout.addWidget(QLabelD("sworznia - d<sub>s</sub>"), 22, 0, 1, 4)
        layout.addWidget(QLabelD("tuleji - d<sub>t</sub>"), 22, 4, 1, 4)
        layout.addWidget(QLabelD("otworów - d<sub>otw</sub>"), 22, 8, 1, 4)
        layout.addWidget(self.input_widgets["d_sw"], 23, 0, 1, 4)
        layout.addWidget(self.input_widgets["d_tul"], 23, 4, 1, 4)
        layout.addWidget(self.obl_srednice_labels[2], 23, 8, 1, 4)

        layout.addWidget(self.results_frame, 24, 0, 6, 12)

    def inputsModified(self) -> None:
        for key in self.input_widgets:
            self.input_dane[key] = self.input_widgets[key].value()

        self.Rwk_label.setText(str(self.input_dane["R_wt"]) + " mm")
        self.recalculate(self.wheel_rotation_angle)

    def recalculate(self, angle: float) -> None:
        self.wheel_rotation_angle = angle
        if not self.module_enabled:
            return

        material_data = self.material_frame.getData()
        wyniki = obliczenia_mech_wyjsciowy(self.input_dane, self.zew_dane, material_data, self.tol_data, self.wheel_rotation_angle)

        self.obliczone_dane["d_sw"] = wyniki["d_s_obl"]
        self.obliczone_dane["d_tul"] = wyniki["d_t_obl"]
        self.obliczone_dane["d_otw"] = wyniki["d_o_obl"]
        self.obliczone_dane["F_max"] = wyniki["F_max"]
        self.obliczone_dane["p_max"] = wyniki["p_max"]
        self.obl_srednice_labels[0].setText(str(wyniki["d_s_obl"]) + " mm")
        self.obl_srednice_labels[1].setText(str(wyniki["d_t_obl"]) + " mm")
        self.obl_srednice_labels[2].setText(str(wyniki["d_o_obl"]) + " mm")
        self.input_widgets["d_sw"].modify(minimum=wyniki["d_s_obl"], maximum=wyniki["d_t_obl"])
        self.input_dane["d_sw"] = self.input_widgets["d_sw"].value()
        self.input_widgets["d_tul"].modify(minimum=wyniki["d_t_obl"], maximum=wyniki["d_o_obl"])
        self.input_dane["d_tul"] = self.input_widgets["d_tul"].value()

        anim_data = {
            "n": self.input_dane["n"],
            "R_wt": self.input_dane["R_wt"],
            "d_sw": self.input_dane["d_sw"],
            "d_tul": self.input_dane["d_tul"],
            "d_otw": self.obliczone_dane["d_otw"],
        }
        if anim_data["R_wt"] + anim_data["d_otw"] / 2 >= self.zew_dane["R_f1"]:
            self.animDataUpdated.emit({"PinOutTab": False})
            self.errorsUpdated.emit({"R_wt duze": True})
        elif sprawdz_przecinanie_otworow(self.input_dane["R_wt"], self.input_dane["n"], self.obliczone_dane["d_otw"]):
            self.animDataUpdated.emit({"PinOutTab": False})
            self.errorsUpdated.emit({"R_wt male": True})
        elif wyniki["p_max"] > material_data["p_dop"]:
            self.animDataUpdated.emit({"PinOutTab": False})
            self.errorsUpdated.emit({"naciski przekroczone": True})
        else:
            self.errorsUpdated.emit(None)
            self.animDataUpdated.emit({"PinOutTab": anim_data})
            self.chartDataUpdated.emit({
                "sily": wyniki["sily"],
                "naciski": wyniki['naciski'],
                "straty": wyniki['straty'],
                "mode": wyniki['mode'],
            })

        self.obliczone_dane["F_wmr"] = round(1000 * 4 * (self.zew_dane["M_wyj"] / self.zew_dane["K"]) / (pi * self.input_dane["R_wt"]), 1)
        self.obliczone_dane["r_mr"] = round(pi * self.input_dane["R_wt"] / 4, 2)
        self.obliczone_dane["N_cmr"] = round(sum(wyniki['straty'][0]), 3)
        self.results_frame.update({"F_max": wyniki["F_max"], "p_max": wyniki["p_max"], "F_wmr": self.obliczone_dane["F_wmr"],
                                   "r_mr": self.obliczone_dane["r_mr"], "N_cmr": self.obliczone_dane["N_cmr"]}, material_data["p_dop"])
        # if should_send_data:
        # zrobie tak bo nie wiem jak wyslac po oddznaczeniu, bo jak sie zmieni K albo M jak jest wylaczone to potem bym nie wyslal jak sie odblokuje
        # TODO: a moze wysyłac ten sygnal/odpalac metode sendData w tej funkcji od zaznaczenia ze chce to, po uzyciu inputsModified
        self.shouldSendData.emit()
    
    def copyDataToInputs(self, new_input_data: Dict) -> None:
        for key in self.input_widgets:
            self.input_widgets[key].blockSignals(True)
            self.input_widgets[key].setValue(new_input_data[key])
            self.input_widgets[key].blockSignals(False)
        self.inputsModified()

    def closeChoiceWindow(self, choice: str) -> None:
        self.input_dane["podparcie"] = choice
        self.ch_var_label.setText(choice)
        self.support_popup.hide()
        self.accept_button.setEnabled(True)

    def toleranceUpdate(self, tol_data: Dict) -> None:
        self.tol_data = tol_data
        self.recalculate(self.wheel_rotation_angle)


class PinOutTab(AbstractTab):
    thisEnabled = Signal(bool)
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        layout = QVBoxLayout()
        button_layout = QGridLayout()
        stacklayout = QStackedLayout()
        layout.addLayout(button_layout)
        layout.addLayout(stacklayout)
        self.use_this_check = QCheckBox(text="Używaj tego mechanizmu wyjściowego")
        self.use_this_check.stateChanged.connect(self.useThisChanged)
        button_layout.addWidget(self.use_this_check, 1, 0, 1, 2)

        help_pdf_button = QPushButton("Pomoc")
        button_layout.addWidget(help_pdf_button, 1, 2)
        help_pdf_button.clicked.connect(lambda: open_pdf("help//mechanizmy-sworzniowe-help-1.pdf"))

        self.data = DataEdit(self)
        self.data.shouldSendData.connect(self.sendData)
        self.wykresy = ResultsTab(self)
        self.tol_edit = ToleranceEdit(self)
        
        self.data.chartDataUpdated.connect(self.wykresy.updateResults)
        self.tol_edit.toleranceDataUpdated.connect(self.data.toleranceUpdate)

        scrollable_tab = ResponsiveContainer(self, self.data, self.data.setupSmallLayout, self.data.setupLayout, 620, 1200)
        tab_titles = ["Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        stacked_widgets = [scrollable_tab, self.wykresy, self.tol_edit]

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button, 0, index)
            stacklayout.addWidget(widget)
            button.pressed.connect(partial(stacklayout.setCurrentIndex, index))

        self.setLayout(layout)
        self.data.setEnabled(False)
        self.tol_edit.setEnabled(False)
    
    def useThisChanged(self, state: bool) -> None:
        self.data.setEnabled(state)
        self.tol_edit.setEnabled(state)
        if state:
            self.thisEnabled.emit(True)
            self.data.module_enabled = True
            self.data.recalculate(self.data.wheel_rotation_angle)
        else:
            self.thisEnabled.emit(False)
            self.data.module_enabled = False
            self.data.animDataUpdated.emit({"PinOutTab": False})

    def useOtherChanged(self, state: bool) -> None:
        self.use_this_check.setEnabled(not state)

    def sendData(self) -> Dict[str, float]:
        M_k = self.data.zew_dane["M_wyj"] / self.data.zew_dane["K"]
        R_wt = self.data.input_dane["R_wt"]
        
        self.dataChanged.emit({"PinOutTab": {
            "F_wmr": 1000 * 4 * M_k / (pi * R_wt),
            "r_mr": pi * R_wt / 4,
        }})
    
    def receiveData(self, new_data: Dict[str, Dict[str, Union[int, float]]]) -> None:
        wanted_data = None
        if new_data.get("GearTab") is not None:
            wanted_data = new_data.get("GearTab")
        elif new_data.get("base") is not None:
            wanted_data = new_data.get("base")
        else:
            return
        
        for key in wanted_data:
            if self.data.zew_dane.get(key) is not None:
                self.data.zew_dane[key] = wanted_data[key]

        if wanted_data.get("K") == 2:
            self.data.label_e2.show()
            self.data.input_widgets["e2"].show()
        elif wanted_data.get("K") == 1:
            self.data.label_e2.hide()
            self.data.input_widgets["e2"].hide()
        
        self.data.recalculate(self.data.wheel_rotation_angle)
        self.sendData()

    def saveData(self) -> Dict:
        self.data.recalculate(self.data.wheel_rotation_angle)
        return {
            "input_dane": self.data.input_dane,
            "zew_dane": self.data.zew_dane,
            "material_data": self.data.material_frame.getData(),
            "tolerancje": self.tol_edit.tolerancje,
            "tol_mode": self.tol_edit.mode,
            "use_tol": self.tol_edit.check.isChecked()
        }

    def loadData(self, new_data: Dict) -> None:
        self.tol_edit.copyDataToInputs(new_data.get("tolerancje"))
        if new_data.get("tol_mode") == "deviations":
            self.tol_edit.tol_check.setChecked(False)
            self.tol_edit.dev_check.setChecked(True)
        else:
            self.tol_edit.tol_check.setChecked(True)
            self.tol_edit.dev_check.setChecked(False)
        self.tol_edit.check.setChecked(new_data.get("use_tol"))

        self.data.material_frame.loadData(new_data.get("material_data"))
        self.data.zew_dane = new_data.get("zew_dane")
        self.data.copyDataToInputs(new_data.get("input_dane"))

    def reportData(self) -> str:
        def indent_point(point_text, bullet, bold, sa=100):
            bullet_code = "\\bullet" if bullet else ""
            bold_code = "\\b" if bold else ""
            return f"{{\\pard\\sa{str(sa)}\\fi-300\\li600{bullet_code}{bold_code}\\tab {point_text} \\par}}"

        if not self.use_this_check.isChecked():
            return ''
        materials = self.data.material_frame.getData()
        wyniki = obliczenia_mech_wyjsciowy(self.data.input_dane, self.data.zew_dane, materials, self.data.tol_data, self.data.wheel_rotation_angle)

        text = "{\\pard\\b Mechanizm wyjściowy \\line\\par}"
        text += "{\\pard\\sa200\\b Dane: \\par}"
        text += indent_point(f"Liczba sworzni z tulejami: n = {self.data.input_dane['n']}", True, True)
        text += indent_point(f"Promień rozmieszczenia sworzni z tulejami: R{{\sub wt}} = {self.data.input_dane['R_wt']} [mm]", True, True)
        if self.data.zew_dane["K"] == 2:
            text += indent_point(f"Odstęp pomiędzy kołami: x = {self.data.input_dane['e2']} [mm]", True, True)
        
        text += "{\\pard\\sa200\\b Materiały: \\par}"
        text += "{\\pard\\sa100 koło cykloidalne: \\par}"
        text += indent_point(f"Materiał: {materials['wheel']['nazwa']}", False, False)
        text += indent_point(f"Moduł Younga: E = {materials['wheel']['E']} [MPa]", False, False)
        text += indent_point(f"Liczba Poissona: v = {materials['wheel']['v']}", False, False)
        text += "{\\pard\\sa100 tuleja: \\par}"
        text += indent_point(f"Materiał: {materials['sleeve']['nazwa']}", False, False)
        text += indent_point(f"Moduł Younga: E = {materials['sleeve']['E']} [MPa]", False, False)
        text += indent_point(f"Liczba Poissona: v = {materials['sleeve']['v']}", False, False)
        text += "{\\pard\\sa100 sworzeń: \\par}"
        text += indent_point(f"Materiał: {materials['pin']['nazwa']}", False, False)
        text += indent_point(f"Granica plastyczności: R{{\sub e}} {materials['pin']['Re']} [MPa]", False, False)
        text += indent_point(f"Współczynnik bezpieczeństwa: k = {materials['pin_sft_coef']}", False, False)
        
        text += f"{{\\pard\\sa100 Współczynnik tarcia tocznego pomiędzy otworami a tulejami: f{{\sub k-t}} = {self.data.input_dane['f_kt']:.5f} [m]\\par}}"
        text += f"{{\\pard\\sa100 Współczynnik tarcia tocznego pomiędzy tulejami a sworzniami: f{{\sub t-s}} = {self.data.input_dane['f_ts']:.5f} [m]\\par}}"
        text += indent_point(f"Nacisk dopuszczalny (dla pary materiałów): p{{\sub dop}} = {materials['p_dop']} [MPa]", False, False)

        text += "{\\pard\\sa200\\b Obliczenia: \\par}"
        text += indent_point("Siły działające na sworzeń:", True, True)
        text += indent_point(f"Maksymalna siła działająca na sworzeń: F{{\sub max}} = {wyniki['F_max']} [N]", False, False)
        text += indent_point(f"Wypadkowa siła w mechanizmie: F{{\sub wmr}} = {self.data.obliczone_dane['F_wmr']} [N]", False, False)
        text += indent_point(f"Ramię działania siły wypadkowej w mechanizmie: r{{\sub mr}} = {self.data.obliczone_dane['r_mr']} [mm]", False, False, 500)
        
        text += indent_point("Geometria mechanizmu wyjściowego:", True, True)
        text += indent_point(f"Sposób podparcia sworznia: {self.data.input_dane['podparcie']}", False, False)
        text += indent_point(f"Obliczona średnica sworznia: d{{\sub sobl}} = {self.data.obliczone_dane['d_sw']} [mm]", False, False)
        text += indent_point(f"Przyjęta średnica sworznia: d{{\sub s}} = {self.data.input_dane['d_sw']} [mm]", False, False)
        text += indent_point(f"Obliczona średnica zewnętrzna tulei: d{{\sub tzobl}} = {self.data.obliczone_dane['d_tul']} [mm]", False, False)
        text += indent_point(f"Przyjęta średnica zewnętrzna tulei: d{{\sub tz}} = {self.data.input_dane['d_tul']} [mm]", False, False)
        text += indent_point(f"Średnica otworu pod tuleje: d{{\sub o}} = {self.data.obliczone_dane['d_otw']} [mm]", False, False, 500)
        
        text += indent_point("Naciski pomiędzy tulejami a otworami:", True, True)
        text += indent_point(f"Maksymalne naciski pomiędzy tuleją a otworem: p{{\sub max}} = {wyniki['p_max']} [MPa]", False, False)
        text += f"{{\\pard\\sa500\\qc Warunek p{{\sub max}} = {wyniki['p_max']} [MPa] < p{{\sub dop}} = {materials['p_dop']} [MPa] został spełniony. \\par}}"
        
        text += indent_point("Moc tracona:", True, True)
        text += indent_point(f"Całkowita strata mocy: N{{\sub Cmr}} = {round(sum(wyniki['straty'][0]), 3)} [W]", False, False, 500)

        a = "{\\trowd\\trleft3200"
        b = "{\\trowd\\trleft4000"
        borders = "\\clbrdrt\\brdrw15\\brdrs\\clbrdrl\\brdrw15\\brdrs\\clbrdrb\\brdrw15\\brdrs\\clbrdrr\\brdrw15\\brdrs\\clvertalc"
        start = "\\pard\\intbl\\qc "
        end = "\\cell"
        endrow = "\\row}"

        text += b + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + "F{\sub j}" + end + start + "p{\sub j}" + end + start + "N{\sub mrj}" + end + endrow
        text += a + borders + "\\cellx4000" + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + "Nr sworznia" + end + start + "[N]" + end + start + "[MPa]" + end + start + "[W]" + end + endrow
        for index, row in enumerate(zip(wyniki["sily"][0], wyniki["naciski"][0], wyniki["straty"][0]), 1):
            text += a + borders + "\\cellx4000" + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + str(index) + end + start + str(row[0]) + end + start + str(row[1]) + end + start + str(row[2]) + end + endrow

        text += "\\line"
        return text

    def csvData(self) -> str:
        if not self.use_this_check.isChecked():
            return ''
        wyniki = obliczenia_mech_wyjsciowy(self.data.input_dane, self.data.zew_dane, self.data.material_frame.getData(), self.data.tol_data, self.data.wheel_rotation_angle)
        title = "Mechanizm wyjściowy ze sworzniami\n"
        sily_text = [f"{i},{wyniki['sily'][0][i]}\n" for i in range(1, len(wyniki['sily']) + 1)]
        naciski_text = [f"{i},{wyniki['naciski'][0][i]}\n" for i in range(1, len(wyniki['naciski']) + 1)]
        straty_text = [f"{i},{wyniki['straty'][0][i]}\n" for i in range(1, len(wyniki['straty']) + 1)]
        return title + "Siły na sworzniach [N]\n".join(sily_text) + "Naciski powierzchniowe na sworzniach [MPa]\n".join(naciski_text) + "Straty mocy na sworzniach [W]\n".join(straty_text) + "\n"
