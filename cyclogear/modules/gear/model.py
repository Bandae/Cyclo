from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget

from common.common_widgets import StatusDiodes
from .calculations import calculate_gear, gear_error_check


class GearModel(QWidget):
    changeDiode = Signal(StatusDiodes.Status)
    chartDataUpdated = Signal(dict)
    animDataUpdated = Signal(dict)
    errorsUpdated = Signal(dict) 
    shouldSendData = Signal()

    def __init__(self):
        super().__init__()
        self.has_visual_error = False
        self.data = {
            "z" : 24,       "ro" : None,
            "lam" : None,   "g" : None,
            "Ra1" : 0,      "Rf1": 0,
            "Rw1": 0,       "Ra2": 0,
            "Rf2": 0,       "Rw2": 0,
            "Rb" : 0,       "Rb2": 0,
            "Rg" : 0,       "sr": 0,
            "e" : 0,        "h" : 0,
            "K" : None,     "nwyj" : 21,
            "b_wheel": None,
            "f_kr": None,   "f_ro": None,
            "F_max": 0,     "p_max": 0,
            "F_wzx": 0,     "F_wzy": 0,
            "F_wz": 0,      "N_Ck-ri": 0,
        }
        self.tolerances = None
        self.outside_data = {
            "i": 24,
            "M_wyj": 500,
            "n_wej": 500,
        }
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
        self.material_data = {
            "p_dop": 450,
            "wheel_mat": self.materials["C30"],
            "roller_mat": self.materials["C30"],
            "wheel_treat": "normalizowanie",
            "roller_treat": "normalizowanie",
        }
    
    def findAllowedPressure(self) -> None:
        wheel_treat = self.material_data["wheel_treat"]
        roller_treat = self.material_data["roller_treat"]
        wheel_p_dop = self.material_data["wheel_mat"]["p_dop_" + wheel_treat]
        roller_p_dop = self.material_data["roller_mat"]["p_dop_" + roller_treat]

        p_dop = self.material_data["p_dop"] = min(wheel_p_dop, roller_p_dop)
        return p_dop
    
    def refillData(self) -> None:
        z=self.data["z"]
        ro=self.data["ro"]
        lam=self.data["lam"]
        g=self.data["g"]
        self.data["Ra1"] = round(ro*(z+1+lam)-g, 3)
        self.data["Rf1"] = round(ro*(z+1-lam)-g, 3)
        self.data["Rw1"] = round(ro*lam*z, 3)
        self.data["Ra2"] = round(ro*(z+1)-g, 3)
        self.data["Rf2"] = self.data["Ra1"]
        self.data["Rw2"] = round(ro*lam*(z+1), 3)
        self.data["Rb"] = round(ro*z, 3)
        self.data["Rg"] = round(ro*(z+1), 3)
        self.data["e"] = round(ro*lam, 3)
        self.data["Rb2"] = self.data["e"]+g+self.data["Rf1"]
        self.data["h"] = 2*self.data["e"]
        self.data["sr"] = round((2*g)+(2*self.data["Rb2"]), 2)
    
    def recalculate(self) -> None:
        results = calculate_gear(self.data, self.material_data, self.outside_data, self.tolerances)
        for key in results:
            if key in self.data:
                self.data[key] = results[key]

        self.chartDataUpdated.emit({
            "sily": results["sily"],
            "naciski": results["naciski"],
            "straty": results["straty"],
            "luzy": results["luzy"],
        })

        self.sendAnimationData()
        if self.has_visual_error:
            return
        
        self.shouldSendData.emit()
        self.changeDiode.emit(StatusDiodes.Status.OK)
        if results["p_max"] > self.material_data["p_dop"]:
            self.changeDiode.emit(StatusDiodes.Status.ERROR)
            self.errorsUpdated.emit({"naciski przekroczone": True})
    
    def sendAnimationData(self) -> None:
        errors = gear_error_check(self.data["z"], self.data["lam"], self.data["g"], self.data["e"], self.data["Rg"], self.data["ro"])
        self.errorsUpdated.emit(errors)

        if errors:
            self.has_visual_error = True
            self.changeDiode.emit(StatusDiodes.Status.ERROR)
            self.animDataUpdated.emit({"GearTab": False})
        else:
            self.has_visual_error = False
            self.changeDiode.emit(StatusDiodes.Status.WARNING)
            self.animDataUpdated.emit({"GearTab": self.data.copy()})
