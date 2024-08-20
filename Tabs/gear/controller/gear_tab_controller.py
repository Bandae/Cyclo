
import math

from ..view.gear_tab import GearTab
from ..model.gear_calc import calculate_gear

from ...common.Itab_controller import ITabController
from common.utils import open_pdf

class GearTabController(ITabController):
    def __init__(self, gear_tab: GearTab):
        self.tab = gear_tab

        self.connect_signals_and_slots()
    
    def connect_signals_and_slots(self):
        self.tab.data.shouldSendData.connect(self.sendData)
        self.tab.data.chartDataUpdated.connect(self.tab.wykresy.updateResults)
        self.tab.tolerance_edit.toleranceDataUpdated.connect(self.tab.data.toleranceUpdate)
        self.tab.help_pdf_button.clicked.connect(lambda: open_pdf("help//zazebienie-help-1.pdf"))

    def sendData(self) -> None:
        material_data = self.tab.data.dane_materialowe.getData()
        self.tab.dataChanged.emit({"GearTab": {
            "R_w1": self.tab.data.dane_all["Rw1"],
            "R_f1": self.tab.data.dane_all["Rf1"],
            "e": self.tab.data.dane_all["e"],
            "K": self.tab.data.dane_all["K"],
            "B": material_data["b_wheel"],
        }})
    
    def receiveData(self, new_data) -> None:
        base_data = new_data.get("base")
        if base_data is None:
            return
        calculate = not self.tab.data.accept_button.isEnabled()
        self.tab.data.baseDataChanged(base_data, calculate)
    
    def saveData(self):
        self.tab.data.inputsModified(True)
        return {
            "dane_all": self.tab.data.dane_all,
            "material_data": self.tab.data.dane_materialowe.getData(),
        }

    def loadData(self, new_data) -> None:
        if new_data is None:
            return
        self.tab.data.copyDataToInputs(new_data["dane_all"])
        self.tab.data.dane_materialowe.copyDataToInputs(new_data["material_data"])
        self.tab.data.dane_all = new_data["dane_all"]

    def reportData(self) -> str:
        def indent_point(point_text, bullet, bold, sa=100):
            bullet_code = "\\bullet" if bullet else ""
            bold_code = "\\b" if bold else ""
            return f"{{\\pard\\sa{str(sa)}\\fi-300\\li600{bullet_code}{bold_code}\\tab {point_text} \\par}}"

        materials = self.tab.data.dane_materialowe.getData()
        results = calculate_gear(self.tab.data.dane_all, self.tab.data.dane_materialowe.getData(), self.tab.data.outside_data)

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
        text += indent_point(f"Liczba zębów: z{{\sub 1}} = {self.tab.data.dane_all['z']}", False, False)
        text += indent_point(f"Promień (średnica) koła wierzchołkowego: r{{\sub a1}} = {self.tab.data.dane_all['Ra1']} ({self.tab.data.dane_all['Ra1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła stóp: r{{\sub f1}} = {self.tab.data.dane_all['Rf1']} ({self.tab.data.dane_all['Rf1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła tocznego: r{{\sub w1}} = {self.tab.data.dane_all['Rw1']} ({self.tab.data.dane_all['Rw1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła zasadniczego: r{{\sub b1}} = {self.tab.data.dane_all['Rb']} ({self.tab.data.dane_all['Rb'] * 2}) [mm]", False, False)
        text += indent_point(f"Wysokość zęba: h = {self.tab.data.dane_all['h']} [mm]", False, False)
        text += indent_point(f"Szerokość koła: B = {materials['b_wheel']} [mm]", False, False)

        text += "{\\pard\\sa100 - koło współpracujące: \\par}"
        text += indent_point(f"Liczba zębów (rolek): z{{\sub 2}} = {self.tab.data.dane_all['z'] + 1}", False, False)
        text += indent_point(f"Promień (średnica) rolki: r{{\sub r}} = {self.tab.data.dane_all['g']} ({self.tab.data.dane_all['g'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) rozmieszczenia rolek: r{{\sub b2}} = {self.tab.data.dane_all['Rb2']} ({self.tab.data.dane_all['Rb2'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła tocznego: r{{\sub w2}} = {self.tab.data.dane_all['Rw2']} ({self.tab.data.dane_all['Rw2'] * 2}) [mm]", False, False)
        text += indent_point(f"Mimośród: e = {self.tab.data.dane_all['e']} [mm]", False, False, 500)

        text += indent_point("Siły międzyzębne:", True, True)
        text += indent_point(f"Maksymalna siła międzyzębna: F{{\sub max}} = {results['F_max']} [N]", False, False)
        text += indent_point(f"Całkowita siła międzyzębna dla osi 0X: F{{\sub wzx}} = {results['F_wzx']} [N]", False, False)
        text += indent_point(f"Całkowita siła międzyzębna dla osi 0Y: F{{\sub wzy}} = {results['F_wzy']} [N]", False, False)
        text += indent_point(f"Całkowita wypadkowa siła międzyzębna: F{{\sub wz}} = {results['F_wz']} [N]", False, False, 500)
        text += indent_point("Naciski międzyzębne:", True, True)
        text += indent_point(f"Maksymalne naciski międzyzębne: p{{\sub max}} = {results['p_max']} [MPa]", False, False)
        text += f"{{\\pard\\sa500\\qc Warunek p{{\sub max}} = {results['p_max']} [MPa] < p{{\sub dop}} = {materials['p_dop']} [MPa] został spełniony. \\par}}"

        text += indent_point("Moc tracona:", True, True)
        text += indent_point(f"Prędkość kątowa wałka czynnego: \\uc1\\u969*{{\sub wej}} = {round(math.pi * self.tab.data.outside_data['n_wej'] / 30, 2)} [rad/s]", False, False)
        text += indent_point(f"Całkowita strata mocy: N{{\sub Ck-r}} = {round(sum(results['straty'][0]), 3)} [W]", False, False)
        text += indent_point(f"Prędkość obrotowa wałka biernego: n{{\sub wyj}} = {self.tab.data.dane_all['nwyj']} [obr/min]", False, False)
        text += indent_point(f"Prędkość kątowa wałka biernego: \\uc1\\u969*{{\sub wyj}} = {round(math.pi * self.tab.data.dane_all['nwyj'] / 30, 2)} [rad/s]", False, False, 500)

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
