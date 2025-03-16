from functools import partial
from typing import Dict, Optional, Tuple, Union
import math
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QHBoxLayout, QStackedLayout
from modules.common.abstract_tab import AbstractTab
from common.common_widgets import IntSpinBox, DoubleSpinBox, QLabelD, ResponsiveContainer, StatusDiodes
from modules.common.widgets.tolerance_widgets import ToleranceEdit
from modules.common.widgets.charts import ResultsTab
from .widgets import MaterialFrame, ResultsFrame, VisualsFrame
from .calculations import calculate_gear
from .model import GearModel
from common.utils import open_pdf
#TODO: nie podoba mi się obliczanie p_max, jako po prostu największego nacisku z wszystkich. U wiktora jest p_max wiekszy niz na sworzniu czasem, bo sworzen zmienia p jak sie obraca.


class DataEdit(QWidget):
    changeDiode = Signal(StatusDiodes.Status)
    filledOut = Signal()

    def __init__(self, parent: AbstractTab, model) -> None:
        super().__init__(parent)
        self.model = model

        self.visuals_frame = VisualsFrame(self, model)
        self.material_data = MaterialFrame(self, model)
        self.results_frame = ResultsFrame(self, model)

        self.data_inputs = {
            "B": DoubleSpinBox(self.model.data["B"], 10, 100, 0.5),
            "f_kr": DoubleSpinBox(self.model.data["f_kr"], 0.00001, 0.0001, 0.00001, 5),
            "f_ro": DoubleSpinBox(self.model.data["f_ro"], 0.00001, 0.0001, 0.00001, 5),
        }
        for widget in self.data_inputs.values():
            widget.valueChanged.connect(self.inputsChanged)
        
        self.n_out_label = QLabelD(str(self.model.data["nwyj"]) + " obr/min", style=False)
        self.accept_button = QPushButton("Oblicz")

        self.accept_button.clicked.connect(self.recalculate)
        self.material_data.changed.connect(self.inputsChanged)
        self.visuals_frame.accepted.connect(self.visualsChanged)

        self.data_labels = { key: QLabelD("") for key in ("sr", "Ra1", "R_f1", "R_w1", "Ra2", "Rf2", "Rw2", "Rg", "e", "h") }

        self.label_descriptions = {
            "sr": "Średnica zewnętrzna przekładni",
            "Ra1": "Promień koła wierzchołkowego",
            "R_f1": "Promień koła stóp",
            "R_w1": "Promień koła tocznego",
            "Ra2": "Promień koła wierzchołkowego",
            "Rf2": "Promień koła stóp",
            "Rw2": "Promień koła tocznego",
            "Rg": "Promień rozmieszczenia rolek",
            "e": "Mimośród",
            "h": "Wysokość zęba",
        }

        layout = QGridLayout()
        self.setLayout(layout)
        self.setupSmallLayout(layout)

        # TODO: z jakiegoś powodu używanie self.children() w trakcie init, a nawet na zewnątrz z mainwindow psuje layout.
        # więc jest tak wszystko pokolei
        self.accept_button.setEnabled(False)
        self.results_frame.setEnabled(False)
        self.material_data.setEnabled(False)
        for widget in self.data_inputs.values():
            widget.setEnabled(False)
    
    def setupLayout(self, layout: QGridLayout) -> None:
        layout.addWidget(self.visuals_frame, 0, 0, 6, 3)
        
        layout.addWidget(self.labels["sr"], 7, 0, 1, 2)
        layout.addWidget(self.data_labels["sr"], 7, 2, 1, 1)

        layout.addWidget(self.labels["cyclo_gear_header"], 8, 0, 1, 3)

        index = 0
        for text, qlabel in self.data_labels.items():
            if text in ("Ra1", "R_f1", "R_w1"):
                index += 1
                layout.addWidget(self.labels[text], 8+index, 0, 1, 2)
                layout.addWidget(qlabel, 8+index, 2, 1, 1)
        
        layout.addWidget(self.labels["rollers_header"], 12, 0, 1, 3)
        roller_labels = {text: qlabel for text, qlabel in self.data_labels.items() if text in ("Ra2", "Rf2", "Rw2", "Rg", "e", "h")}
        for index, (text, qlabel) in enumerate(roller_labels.items(), start=1):
            layout.addWidget(self.labels[text], 12+index, 0, 1, 2)
            layout.addWidget(qlabel, 12+index, 2, 1, 1)

        layout.addWidget(self.labels["B"], 0, 3, 1, 4)
        layout.addWidget(self.data_inputs["B"], 0, 7, 1, 2)
        layout.addWidget(self.labels["kinematics_header"], 1, 3, 1, 6)
        layout.addWidget(self.labels["n_out"], 2, 3, 1, 4)
        layout.addWidget(self.n_out_label, 2, 7, 1, 2)
        layout.addWidget(self.labels["f_kr"], 3, 3, 1, 4)
        layout.addWidget(self.data_inputs["f_kr"], 3, 7, 1, 2)
        layout.addWidget(self.labels["f_ro"], 4, 3, 1, 4)
        layout.addWidget(self.data_inputs["f_ro"], 4, 7, 1, 2)

        layout.addWidget(self.material_data, 5, 3, 5, 6)
        layout.addWidget(self.accept_button, 10, 5, 1, 2)
        layout.addWidget(self.results_frame, 11, 5, 7, 4)
    
    def setupSmallLayout(self, layout: QGridLayout) -> None:
        if not hasattr(self, "labels"):
            self.labels = {
                "B": QLabelD("Szerokość koła [mm]:"),
                "kinematics_header": QLabelD("Dane kinematyczne"),
                "n_out": QLabelD("Prędkość obrotowa wyj:"),
                "f_kr": QLabelD("Współczynnik tarcia koło - rolka [m]:"),
                "f_ro": QLabelD("Współczynnik tarcia rolka - obudowa [m]:"),
                "cyclo_gear_header": QLabelD("Obiegowe koło cykloidalne:"),
                "rollers_header": QLabelD("Koło współpracujące:"),
            }
            self.labels.update({key: QLabelD(text) for key, text in self.label_descriptions.items()})
        layout.addWidget(self.visuals_frame, 0, 0, 6, 6)

        layout.addWidget(self.labels["B"], 6, 0, 1, 4)
        layout.addWidget(self.data_inputs["B"], 6, 4, 1, 2)

        layout.addWidget(self.labels["kinematics_header"], 7, 0, 1, 6)
        layout.addWidget(self.labels["n_out"], 8, 0, 1, 4)
        layout.addWidget(self.n_out_label, 8, 4, 1, 2)
        layout.addWidget(self.labels["f_kr"], 9, 0, 1, 4)
        layout.addWidget(self.data_inputs["f_kr"], 9, 4, 1, 2)
        layout.addWidget(self.labels["f_ro"], 10, 0, 1, 4)
        layout.addWidget(self.data_inputs["f_ro"], 10, 4, 1, 2)

        layout.addWidget(self.material_data, 11, 0, 5, 6)
        layout.addWidget(self.accept_button, 16, 0, 1, 6)

        layout.addWidget(self.labels["sr"], 18, 0, 1, 4)
        layout.addWidget(self.data_labels["sr"], 18, 4, 1, 2)
        layout.addWidget(self.labels["cyclo_gear_header"], 19, 0, 1, 6)
        for index, (text, qlabel) in enumerate(self.data_labels.items(), start=1):
            # rozdzielenie na dwie czesci, zeby podpisac co sie tyczy jakiego koła.
            if "1" in text:
                layout.addWidget(self.labels[text], 19+index, 0, 1, 4)
                # layout.addWidget(QLabelD(self.label_descriptions[text]), 19+index, 0, 1, 4)
                layout.addWidget(qlabel, 19+index, 4, 1, 2)
        
        layout.addWidget(self.labels["rollers_header"], 24, 0, 1, 6)
        roller_labels = {text: qlabel for text, qlabel in self.data_labels.items() if text in ("Ra2", "Rf2", "Rw2", "Rg", "e", "h")}
        for index, (text, qlabel) in enumerate(roller_labels.items(), start=1):
            layout.addWidget(self.labels[text], 24+index, 0, 1, 4)
            # layout.addWidget(QLabelD(self.label_descriptions[text]), 24+index, 0, 1, 4)
            layout.addWidget(qlabel, 24+index, 4, 1, 2)

        layout.addWidget(self.results_frame, 31, 0, 6, 6)

    def visualsChanged(self, is_accepted):
        for text, qlabel in self.data_labels.items():
            qlabel.setText(str(round(self.model.data[text], 2)) + " mm")
        
        for child in (child for child in self.children() if child != self.visuals_frame):
            child.setEnabled(is_accepted)
    
    def inputsChanged(self) -> None:
        for key in self.data_inputs:
            self.model.data[key] = self.data_inputs[key].value()
        
        if not all(widget.value() is not None for widget in self.data_inputs.values()): return

        self.accept_button.setEnabled(True)
        self.changeDiode.emit(StatusDiodes.Status.WARNING)
    
    def recalculate(self) -> None:
        self.model.recalculate()
        self.results_frame.update()
        self.accept_button.setEnabled(False)

        self.filledOut.emit()

    def loadData(self, new_input_data: Dict[str, Union[int, float]]) -> None:
        for key, widget in self.data_inputs.items():
            widget.blockSignals(True)
            widget.setValue(new_input_data[key])
            widget.blockSignals(False)
    
    def toleranceUpdate(self, tol_data: Optional[Dict[str, Union[float, Tuple[float, float]]]]) -> None:
        self.model.tolerances = tol_data
        self.recalculate()


class GearTab(AbstractTab):
    wheelMatChanged = Signal(dict, str)
    animDataUpdated = Signal(dict)
    errorsUpdated = Signal(dict)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.model = GearModel()
        
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.diodes = StatusDiodes(self, ("Stan: Wystąpił błąd", "Stan: Niezaakceptowane zmiany w obliczeniach", "Stan: Zarys zaakceptowany", ""))
        self.diodes.enableDiode(StatusDiodes.Status.WARNING)
        layout.addWidget(self.diodes)

        stacklayout = QStackedLayout()
        layout.addLayout(stacklayout)

        self.data = DataEdit(self, self.model)
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
        
        self.model.shouldSendData.connect(self.sendData)
        self.model.chartDataUpdated.connect(self.wykresy.updateResults)
        self.model.animDataUpdated.connect(self.animDataUpdated.emit)
        self.model.errorsUpdated.connect(self.errorsUpdated.emit)
        self.model.changeDiode.connect(self.diodes.enableDiode)
        self.data.material_data.wheelMatChanged.connect(self.wheelMatChanged.emit)
        self.data.filledOut.connect(self.filledOut.emit)
        self.tolerance_edit.toleranceDataUpdated.connect(self.data.toleranceUpdate)

        help_pdf_button = QPushButton("Pomoc")
        button_layout.addWidget(help_pdf_button)
        help_pdf_button.clicked.connect(lambda: open_pdf("help_docs/zazebienie-help-1.pdf"))

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
        self.dataChanged.emit({"GearTab": {key: self.model.data[key] for key in ["R_w1", "R_f1", "F_wzx", "F_wzy", "e", 'n_k', "B"] if self.model.data[key] is not None}})
    
    def receiveData(self, new_data) -> None:
        base_data = new_data.get("base")
        if base_data is None:
            return
        self.data.visuals_frame.baseDataChanged(base_data)
        self.data.n_out_label.setText(str(self.model.data["nwyj"]) + " obr/min")
    
    def saveData(self):
        return {
            "model_data": self.model.saveData(),
            "visual_frame_accepted": self.data.visuals_frame.is_accepted,
            "module_accepted": not self.data.accept_button.isEnabled(),
            "tolerance_input_state": self.tolerance_edit.saveData(),
            "tol_mode": self.tolerance_edit.mode,
            "use_tol": self.tolerance_edit.check.isChecked()
        }

    def loadData(self, new_data) -> None:
        if new_data is None:
            return
        self.model.loadData(new_data["model_data"])
        self.data.visuals_frame.loadData(new_data["model_data"]["data"])
        self.data.loadData(new_data["model_data"]["data"])
        self.data.material_data.loadData(new_data["model_data"]["material_data"])

        if new_data["visual_frame_accepted"]:
            self.data.visuals_frame.okClicked()
        if new_data["module_accepted"]:
            self.data.recalculate()

        self.model.loadData(new_data["model_data"])

        self.tolerance_edit.loadData(new_data.get("tolerance_input_state"), new_data.get("tol_mode"), new_data.get("use_tol"))
    
    def reportData(self) -> str:
        def indent_point(point_text, bullet, bold, sa=100):
            bullet_code = "\\bullet" if bullet else ""
            bold_code = "\\b" if bold else ""
            return f"{{\\pard\\sa{str(sa)}\\fi-300\\li600{bullet_code}{bold_code}\\tab {point_text} \\par}}"

        materials = self.model.material_data
        results = calculate_gear(self.model.data, self.model.material_data, self.model.outside_data)

        text = "{\\pard\\b Zazębienie \\line\\par}"
        text += indent_point("Materiały", True, True)
        text += "{\\pard\\sa100 - koło podstawowe: \\par}"
        text += indent_point(f"Materiał: {materials['wheel_mat']['nazwa']}", False, False)
        text += indent_point(f"Moduł Younga: E = {materials['wheel_mat']['E']} [MPa]", False, False)
        text += indent_point(f"Liczba Poissona: v = {materials['wheel_mat']['v']}", False, False)
        text += "{\\pard\\sa100 - koło współpracujące (rolki): \\par}"
        text += indent_point(f"Materiał: {materials['roller_mat']['nazwa']}", False, False)
        text += indent_point(f"Moduł Younga: E = {materials['roller_mat']['E']} [MPa]", False, False)
        text += indent_point(f"Liczba Poissona: v = {materials['roller_mat']['v']}", False, False)

        text += f"{{\\pard\\sa100 Nacisk dopuszczalny (dla pary materiałów): p{{\sub dop}} = {materials['p_dop']} [MPa]\\par}}"
        text += f"{{\\pard\\sa100 Współczynnik tarcia tocznego pomiędzy zarysem koła a rolkami: f{{\sub k-r}} = {self.model.data['f_kr']:.5f} [m]\\par}}"
        text += f"{{\\pard\\sa500 Współczynnik tarcia tocznego pomiędzy rolkami a obudową: f{{\sub r-o}} = {self.model.data['f_ro']:.5f} [m]\\par}}"

        text += "{\\pard\\sa200\\b Obliczenia: \\par}"
        text += indent_point("Geometria kół:", True, True)
        text += "{\\pard\\sa100 - koło podstawowe: \\par}"
        text += indent_point(f"Liczba zębów: z{{\sub 1}} = {self.model.data['z']}", False, False)
        text += indent_point(f"Promień (średnica) koła wierzchołkowego: r{{\sub a1}} = {self.model.data['Ra1']} ({self.model.data['Ra1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła stóp: r{{\sub f1}} = {self.model.data['R_f1']} ({self.model.data['R_f1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła tocznego: r{{\sub w1}} = {self.model.data['R_w1']} ({self.model.data['R_w1'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła zasadniczego: r{{\sub b1}} = {self.model.data['Rb']} ({self.model.data['Rb'] * 2}) [mm]", False, False)
        text += indent_point(f"Wysokość zęba: h = {self.model.data['h']} [mm]", False, False)
        text += indent_point(f"Szerokość koła: B = {self.model.data['B']} [mm]", False, False)

        text += "{\\pard\\sa100 - koło współpracujące: \\par}"
        text += indent_point(f"Liczba zębów (rolek): z{{\sub 2}} = {self.model.data['z'] + 1}", False, False)
        text += indent_point(f"Promień (średnica) rolki: r{{\sub r}} = {self.model.data['g']} ({self.model.data['g'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) rozmieszczenia rolek: r{{\sub b2}} = {self.model.data['Rb2']} ({self.model.data['Rb2'] * 2}) [mm]", False, False)
        text += indent_point(f"Promień (średnica) koła tocznego: r{{\sub w2}} = {self.model.data['Rw2']} ({self.model.data['Rw2'] * 2}) [mm]", False, False)
        text += indent_point(f"Mimośród: e = {self.model.data['e']} [mm]", False, False, 500)

        text += indent_point("Siły międzyzębne:", True, True)
        text += indent_point(f"Maksymalna siła międzyzębna: F{{\sub max}} = {results['F_max']} [N]", False, False)
        text += indent_point(f"Całkowita siła międzyzębna dla osi 0X: F{{\sub wzx}} = {results['F_wzx']} [N]", False, False)
        text += indent_point(f"Całkowita siła międzyzębna dla osi 0Y: F{{\sub wzy}} = {results['F_wzy']} [N]", False, False)
        text += indent_point(f"Całkowita wypadkowa siła międzyzębna: F{{\sub wz}} = {results['F_wz']} [N]", False, False, 500)
        text += indent_point("Naciski międzyzębne:", True, True)
        text += indent_point(f"Maksymalne naciski międzyzębne: p{{\sub max}} = {results['p_max']} [MPa]", False, False)
        text += f"{{\\pard\\sa500\\qc Warunek p{{\sub max}} = {results['p_max']} [MPa] < p{{\sub dop}} = {materials['p_dop']} [MPa] został spełniony. \\par}}"

        text += indent_point("Moc tracona:", True, True)
        text += indent_point(f"Prędkość kątowa wałka czynnego: \\uc1\\u969*{{\sub wej}} = {round(math.pi * self.model.outside_data['n_wej'] / 30, 2)} [rad/s]", False, False)
        text += indent_point(f"Całkowita strata mocy: N{{\sub Ck-r}} = {round(sum(results['straty'][0]), 3)} [W]", False, False)
        text += indent_point(f"Prędkość obrotowa wałka biernego: n{{\sub wyj}} = {self.model.data['nwyj']} [obr/min]", False, False)
        text += indent_point(f"Prędkość kątowa wałka biernego: \\uc1\\u969*{{\sub wyj}} = {round(math.pi * self.model.data['nwyj'] / 30, 2)} [rad/s]", False, False, 500)

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
