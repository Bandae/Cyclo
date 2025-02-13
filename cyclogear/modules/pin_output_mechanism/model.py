from math import pi
from typing import Optional, Union

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget

from common.common_widgets import StatusDiodes
from .calculations import obliczenia_mech_wyjsciowy
from .utils import sprawdz_przecinanie_otworow


class PinOutputMechanismModel(QWidget):
    changeDiode = Signal(StatusDiodes.Status)
    chartDataUpdated = Signal(dict)
    animDataUpdated = Signal(dict)
    errorsUpdated = Signal(dict)
    shouldSendData = Signal()

    def __init__(self):
        super().__init__()
        self.wheel_rotation_angle = 0
        self.module_enabled = False
        self.has_error = False
        self.tol_data = None
        self.input_dane = {
            "n": None,
            "R_wt": None,
            "podparcie": None,
            "d_sw": 5,
            "d_tul": 6,
            "wsp_k": 1.2,
            "e1": None,
            "e2": None,
            "f_kt": None,
            "f_ts": None,
            "f_kt": None,
            "f_ts": None,
        }
        self.obliczone_dane = {
            "d_sw": None,
            "d_tul": None,
            "d_otw": 13.24,
            "F_max": None,
            "p_max": None,
            "F_wmr": None,
            "r_mr": None,
            "N_cmr": None,
        }
        self.zew_dane = {
            "R_w1": 72,
            "R_f1": 107,
            "e": 3.62,
            "K": 2,
            "B": 20,
            "M_wyj": 500,
            "n_wej": 500,
        }
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
        self.material_data = {
            "pin_safety_coef": 2,
            "p_dop": 450,
            "pin_mat": self.materials["15HN"],
            "sleeve_mat": self.materials["C45"],
            "sleeve_treat": "normalizowanie",
            "wheel_mat": self.materials["C30"],
            "wheel_treat": "normalizowanie"
        }
    
    def findAllowedPressure(self):
        wheel_material = self.material_data["wheel_mat"]
        sleeve_material = self.material_data["sleeve_mat"]
        sleeve_treat = self.material_data["sleeve_treat"]
        wheel_treat = self.material_data["wheel_treat"]
        wheel_tempered = wheel_material["type"] == "steel" and wheel_treat == "ulepszanie cieplne"

        p_dop = 0
        if sleeve_material["nazwa"] == "B 101" and wheel_tempered:
            p_dop = 320
        elif sleeve_material["nazwa"] == "B 101" and not wheel_tempered:
            p_dop = 210
        elif sleeve_material["nazwa"] == "B 102" and wheel_tempered:
            p_dop = 320
        elif sleeve_material["nazwa"] == "B 102" and not wheel_tempered:
            p_dop = 215
        elif sleeve_material["nazwa"] == "BA 1044" and wheel_tempered:
            p_dop = 495
        elif sleeve_material["nazwa"] == "BA 1044" and not wheel_tempered:
            p_dop = 330
        else:
            wheel_p_dop = wheel_material["p_dop_" + wheel_treat]
            sleeve_p_dop = sleeve_material["p_dop_" + sleeve_treat]
            p_dop = min(sleeve_p_dop, wheel_p_dop)
        
        self.material_data["p_dop"] = p_dop
    
    def recalculate(self, input_values) -> None:
        for key in input_values:
            self.input_dane[key] = input_values[key]

        wyniki = obliczenia_mech_wyjsciowy(self.input_dane, self.zew_dane, self.material_data, self.tol_data, self.wheel_rotation_angle)

        self.obliczone_dane["d_sw"] = wyniki["d_s_obl"]
        self.obliczone_dane["d_tul"] = wyniki["d_t_obl"]
        self.obliczone_dane["d_otw"] = wyniki["d_o_obl"]
        self.obliczone_dane["F_max"] = wyniki["F_max"]
        self.obliczone_dane["p_max"] = wyniki["p_max"]

        # self.input_dane["d_sw"] = wyniki["d_s_obl"] if self.input_dane["d_sw"] < wyniki["d_s_obl"] else self.input_dane["d_sw"]
        # self.input_dane["d_tul"] = wyniki["d_t_obl"] if self.input_dane["d_tul"] < wyniki["d_t_obl"] else self.input_dane["d_tul"]
        self.input_dane["d_sw"] = self.input_dane["d_sw"] if self.input_dane["d_sw"] is not None and self.input_dane["d_sw"] >= wyniki["d_s_obl"] else wyniki["d_s_obl"]
        self.input_dane["d_tul"] = self.input_dane["d_tul"] if self.input_dane["d_tul"] is not None and self.input_dane["d_tul"] >= wyniki["d_t_obl"] else wyniki["d_t_obl"]

        no_errors = self.sendAnimationUpdates(self.input_dane["n"], self.input_dane["R_wt"], wyniki["p_max"], self.material_data["p_dop"])
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

        # if should_send_data:
        # zrobie tak bo nie wiem jak wyslac po oddznaczeniu, bo jak sie zmieni K albo M jak jest wylaczone to potem bym nie wyslal jak sie odblokuje
        # TODO: a moze wysyłac ten sygnal/odpalac metode sendData w tej funkcji od zaznaczenia ze chce to, po uzyciu inputsModified
        self.shouldSendData.emit()
        if no_errors:
            self.changeDiode.emit(StatusDiodes.Status.OK)
        return {"d_s_obl": wyniki["d_s_obl"], "d_t_obl": wyniki["d_t_obl"], "d_o_obl": wyniki["d_o_obl"], "p_dop": self.material_data["p_dop"], "F_max": wyniki["F_max"], "p_max": wyniki["p_max"],}
    
    def sendAnimationUpdates(self, n, R_wt, p_max: Optional[Union[int, float]]=None, p_dop: Optional[Union[int, float]]=None) -> bool:
        if not n or not R_wt or not self.input_dane["d_sw"]: return
        anim_data = {
            "n": n,
            "R_wt": R_wt,
            "d_sw": self.input_dane["d_sw"],
            "d_tul": self.input_dane["d_tul"],
            "d_otw": self.obliczone_dane["d_otw"],
        }
        if anim_data["R_wt"] + anim_data["d_otw"] / 2 >= self.zew_dane["R_f1"]:
            self.animDataUpdated.emit({"PinOutTab": False})
            self.errorsUpdated.emit({"R_wt duze": True})
        elif sprawdz_przecinanie_otworow(R_wt, n, self.obliczone_dane["d_otw"]):
            self.animDataUpdated.emit({"PinOutTab": False})
            self.errorsUpdated.emit({"R_wt male": True})
        elif p_max is not None and p_max > p_dop:
            self.errorsUpdated.emit({"naciski przekroczone": True})
        else:
            self.errorsUpdated.emit(None)
            self.animDataUpdated.emit({"PinOutTab": anim_data})
            self.changeDiode.emit(StatusDiodes.Status.WARNING)
            self.has_error = False
            return True
        self.changeDiode.emit(StatusDiodes.Status.ERROR)
        self.has_error = True
        return False
