from math import pi
from typing import Dict, Optional, Union, Tuple

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton

from tabs.common.widgets.abstract_tab import AbstractTab
from common.common_widgets import DoubleSpinBox, QLabelD, IntSpinBox

from .popups import SupportWin
from ...model.tuleje_obl import obliczenia_mech_wyjsciowy
from .utils import sprawdz_przecinanie_otworow
from .widgets import ResultsFrame, MaterialsFrame

class EntryDataTab(QWidget):
    chartDataUpdated = Signal(dict)
    animDataUpdated = Signal(dict)
    errorsUpdated = Signal(dict)
    shouldSendData = Signal()

    def __init__(self, parent: AbstractTab) -> None:
        super().__init__(parent)
        self.wheel_rotation_angle = 0
        self.module_enabled = False
        self.tol_data = None
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
            "d_sw": DoubleSpinBox(self.input_dane["d_sw"], 5, step=0.1),
            "d_tul": DoubleSpinBox(self.input_dane["d_tul"], 5, step=0.1),
            "f_kt": DoubleSpinBox(self.input_dane["f_kt"], 0.00001, 0.0001, 0.00001, 5),
            "f_ts": DoubleSpinBox(self.input_dane["f_ts"], 0.00001, 0.0001, 0.00001, 5),
        }

        def inputsAboveAcceptChanged():
            self.accept_button.setEnabled(True)
            for key in ["d_sw", "d_tul", "wsp_k"]:
                self.input_widgets[key].setEnabled(False)
        
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
        self.accept_button.setEnabled(False)
        self.accept_button.clicked.connect(lambda: self.recalculate())

        for key in self.input_widgets:
            if key in ["d_sw", "d_tul", "wsp_k"]:
                self.input_widgets[key].valueChanged.connect(lambda: self.recalculate())
            else:
                self.input_widgets[key].valueChanged.connect(inputsAboveAcceptChanged)
                if key in ["n", "R_wt"]:
                    self.input_widgets[key].valueChanged.connect(lambda: self.sendAnimationUpdates())
                    
        self.material_frame.updated.connect(inputsAboveAcceptChanged)
        
        layout = QGridLayout()
        self.setupSmallLayout(layout)
        self.setLayout(layout)
        self.recalculate()
    
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

    def sendAnimationUpdates(self, p_max: Optional[Union[int, float]]=None, p_dop: Optional[Union[int, float]]=None) -> bool:
        anim_data = {
            "n": self.input_widgets["n"].value(),
            "R_wt": self.input_widgets["R_wt"].value(),
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
        elif p_max is not None and p_max > p_dop:
            self.animDataUpdated.emit({"PinOutTab": False})
            self.errorsUpdated.emit({"naciski przekroczone": True})
        else:
            self.errorsUpdated.emit(None)
            self.animDataUpdated.emit({"PinOutTab": anim_data})
            return True
        return False

    def recalculate(self, angle: float=None) -> None:
        if angle:
            self.wheel_rotation_angle = angle
        if not self.module_enabled:
            return
        
        for key in self.input_widgets:
            self.input_dane[key] = self.input_widgets[key].value()
        self.Rwk_label.setText(str(self.input_dane["R_wt"]) + " mm")

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
        self.input_widgets["d_sw"].modify(minimum=wyniki["d_s_obl"])
        self.input_dane["d_sw"] = self.input_widgets["d_sw"].value()
        self.input_widgets["d_tul"].modify(minimum=wyniki["d_t_obl"])
        self.input_dane["d_tul"] = self.input_widgets["d_tul"].value()

        no_errors = self.sendAnimationUpdates(wyniki["p_max"], material_data["p_dop"])
        if no_errors:
            self.chartDataUpdated.emit({
                "sily": wyniki["sily"],
                "naciski": wyniki["naciski"],
                "straty": wyniki["straty"],
                "luzy": wyniki["luzy"],
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
        self.accept_button.setEnabled(False)
        for key in ["d_sw", "d_tul", "wsp_k"]:
            self.input_widgets[key].setEnabled(True)

    def copyDataToInputs(self, new_input_data: Dict[str, Union[int, float]]) -> None:
        for key in self.input_widgets:
            self.input_widgets[key].blockSignals(True)
            self.input_widgets[key].setValue(new_input_data[key])
            self.input_widgets[key].blockSignals(False)
        self.recalculate()

    def closeChoiceWindow(self, choice: str) -> None:
        self.input_dane["podparcie"] = choice
        self.ch_var_label.setText(choice)
        self.support_popup.hide()
        self.accept_button.setEnabled(True)

    def toleranceUpdate(self, tol_data: Optional[Dict[str, Union[float, Tuple[float, float]]]]) -> None:
        self.tol_data = tol_data
        self.recalculate()
