from math import pi
from typing import Dict, Optional, Union

from ..view.pin_out_tab import PinOutTab
from ...common.Itab_controller import ITabController

from ..model.tuleje_obl import obliczenia_mech_wyjsciowy
from common.utils import open_pdf

class PinOutTabController(ITabController):
    def __init__(self, pin_out_tab: PinOutTab):
        self.tab = pin_out_tab

        self.connect_signals_and_slots()

    def connect_signals_and_slots(self):
        self.tab.data.shouldSendData.connect(self.sendData)
        self.tab.data.chartDataUpdated.connect(self.tab.wykresy.updateResults)
        self.tab.tol_edit.toleranceDataUpdated.connect(self.tab.data.toleranceUpdate)
        self.tab.help_pdf_button.clicked.connect(lambda: open_pdf("mechanizmy-sworzniowe-help-1.pdf"))

    def sendData(self) -> None:
        M_k = self.tab.data.zew_dane["M_wyj"] / self.tab.data.zew_dane["K"]
        R_wt = self.tab.data.input_dane["R_wt"]
        
        self.tab.dataChanged.emit({"PinOutTab": {
            "F_wmr": 1000 * 4 * M_k / (pi * R_wt),
            "r_mr": pi * R_wt / 4,
        }})

    def receiveData(self, new_data: Dict[str, Optional[Dict[str, Union[int, float]]]]) -> None:
        wanted_data = None
        if new_data.get("GearTab") is not None:
            wanted_data = new_data.get("GearTab")
        elif new_data.get("base") is not None:
            wanted_data = new_data.get("base")
        else:
            return
        
        for key in wanted_data:
            if self.tab.data.zew_dane.get(key) is not None:
                self.tab.data.zew_dane[key] = wanted_data[key]

        # if wanted_data.get("K") == 2:
        #     self.tab.data.label_e2.show()
        #     self.tab.data.input_widgets["e2"].show()
        # elif wanted_data.get("K") == 1:
        #     self.tab.data.label_e2.hide()
        #     self.tab.data.input_widgets["e2"].hide()
        if self.tab.data.accept_button.isEnabled():
            self.tab.data.sendAnimationUpdates()
        else:
            self.tab.data.recalculate()
        
        self.sendData()

    def saveData(self) -> Dict:
        self.tab.data.recalculate()
        return {
            "input_dane": self.tab.data.input_dane,
            "zew_dane": self.tab.data.zew_dane,
            "material_data": self.tab.data.material_frame.getData(),
            "tolerancje": self.tab.tol_edit.tolerancje,
            "tol_mode": self.tab.tol_edit.mode,
            "use_tol": self.tab.tol_edit.check.isChecked()
        }

    def loadData(self, new_data: Dict) -> None:
        self.tab.tol_edit.copyDataToInputs(new_data.get("tolerancje"))
        if new_data.get("tol_mode") == "deviations":
            self.tab.tol_edit.tol_check.setChecked(False)
            self.tab.tol_edit.dev_check.setChecked(True)
        else:
            self.tab.tol_edit.tol_check.setChecked(True)
            self.tab.tol_edit.dev_check.setChecked(False)
        self.tab.tol_edit.check.setChecked(new_data.get("use_tol"))

        self.tab.data.material_frame.loadData(new_data.get("material_data"))
        self.tab.data.zew_dane = new_data.get("zew_dane")
        self.tab.data.copyDataToInputs(new_data.get("input_dane"))

    def reportData(self) -> str:
        def indent_point(point_text, bullet, bold, sa=100):
            bullet_code = "\\bullet" if bullet else ""
            bold_code = "\\b" if bold else ""
            return f"{{\\pard\\sa{str(sa)}\\fi-300\\li600{bullet_code}{bold_code}\\tab {point_text} \\par}}"

        if not self.tab.use_this_check.isChecked():
            return ''
        materials = self.tab.data.material_frame.getData()
        wyniki = obliczenia_mech_wyjsciowy(self.tab.data.input_dane, self.tab.data.zew_dane, materials, self.tab.data.tol_data, self.tab.data.wheel_rotation_angle)

        text = "{\\pard\\b Mechanizm wyjściowy \\line\\par}"
        text += "{\\pard\\sa200\\b Dane: \\par}"
        text += indent_point(f"Liczba sworzni z tulejami: n = {self.tab.data.input_dane['n']}", True, True)
        text += indent_point(f"Promień rozmieszczenia sworzni z tulejami: R{{\sub wt}} = {self.tab.data.input_dane['R_wt']} [mm]", True, True)
        if self.tab.data.zew_dane["K"] == 2:
            text += indent_point(f"Odstęp pomiędzy kołami: x = {self.tab.data.input_dane['e2']} [mm]", True, True)
        
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
        
        text += f"{{\\pard\\sa100 Współczynnik tarcia tocznego pomiędzy otworami a tulejami: f{{\sub k-t}} = {self.tab.data.input_dane['f_kt']:.5f} [m]\\par}}"
        text += f"{{\\pard\\sa100 Współczynnik tarcia tocznego pomiędzy tulejami a sworzniami: f{{\sub t-s}} = {self.tab.data.input_dane['f_ts']:.5f} [m]\\par}}"
        text += indent_point(f"Nacisk dopuszczalny (dla pary materiałów): p{{\sub dop}} = {materials['p_dop']} [MPa]", False, False)

        text += "{\\pard\\sa200\\b Obliczenia: \\par}"
        text += indent_point("Siły działające na sworzeń:", True, True)
        text += indent_point(f"Maksymalna siła działająca na sworzeń: F{{\sub max}} = {wyniki['F_max']} [N]", False, False)
        text += indent_point(f"Wypadkowa siła w mechanizmie: F{{\sub wmr}} = {self.tab.data.obliczone_dane['F_wmr']} [N]", False, False)
        text += indent_point(f"Ramię działania siły wypadkowej w mechanizmie: r{{\sub mr}} = {self.tab.data.obliczone_dane['r_mr']} [mm]", False, False, 500)
        
        text += indent_point("Geometria mechanizmu wyjściowego:", True, True)
        text += indent_point(f"Sposób podparcia sworznia: {self.tab.data.input_dane['podparcie']}", False, False)
        text += indent_point(f"Obliczona średnica sworznia: d{{\sub sobl}} = {self.tab.data.obliczone_dane['d_sw']} [mm]", False, False)
        text += indent_point(f"Przyjęta średnica sworznia: d{{\sub s}} = {self.tab.data.input_dane['d_sw']} [mm]", False, False)
        text += indent_point(f"Obliczona średnica zewnętrzna tulei: d{{\sub tzobl}} = {self.tab.data.obliczone_dane['d_tul']} [mm]", False, False)
        text += indent_point(f"Przyjęta średnica zewnętrzna tulei: d{{\sub tz}} = {self.tab.data.input_dane['d_tul']} [mm]", False, False)
        text += indent_point(f"Średnica otworu pod tuleje: d{{\sub o}} = {self.tab.data.obliczone_dane['d_otw']} [mm]", False, False, 500)
        
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
            text += a + borders + "\\cellx4000" + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + str(index) + end + start + "{:.1f}".format(row[0]) + end + start + "{:.2f}".format(row[1]) + end + start + "{:.3f}".format(row[2]) + end + endrow

        text += "\\line"
        return text

    def csvData(self) -> str:
        if not self.tab.use_this_check.isChecked():
            return ''
        wyniki = obliczenia_mech_wyjsciowy(self.tab.data.input_dane, self.tab.data.zew_dane, self.tab.data.material_frame.getData(), self.tab.data.tol_data, self.tab.data.wheel_rotation_angle)
        title = "Mechanizm wyjściowy ze sworzniami\n"
        sily_text = [f"{i},{round(wyniki['sily'][0][i], 1)}\n" for i in range(1, len(wyniki['sily']) + 1)]
        naciski_text = [f"{i},{round(wyniki['naciski'][0][i], 2)}\n" for i in range(1, len(wyniki['naciski']) + 1)]
        straty_text = [f"{i},{round(wyniki['straty'][0][i], 3)}\n" for i in range(1, len(wyniki['straty']) + 1)]
        return title + "Siły na sworzniach [N]\n".join(sily_text) + "Naciski powierzchniowe na sworzniach [MPa]\n".join(naciski_text) + "Straty mocy na sworzniach [W]\n".join(straty_text) + "\n"
