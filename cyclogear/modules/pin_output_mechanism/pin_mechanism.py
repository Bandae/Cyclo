from functools import partial
from typing import Dict, Optional, Union, Tuple

from PySide2.QtCore import Signal, Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QStackedLayout, QCheckBox

from modules.common.abstract_tab import AbstractTab
from common.common_widgets import DoubleSpinBox, QLabelD, ResponsiveContainer, StatusDiodes
from common.utils import open_pdf
from modules.common.widgets.tolerance_widgets import ToleranceEdit
from modules.common.widgets.charts import ResultsTab
from .popups import SupportWin
from .calculations import obliczenia_mech_wyjsciowy
from .widgets import ResultsFrame, MaterialsFrame, VisualsFrame
from .model import PinOutputMechanismModel
#TODO: mam przesunięte do tyłu w poziomie punkty wykresów. Pawel też.
# moze jakos usuwac dane z wykresow jak sa bledy?
# po trzy razy wysylam dane w niektorych sytuacjach, np jak sie zaznaczy zeby uzywac tego. Może to jest pętla.
#TODO: moze zrobic w animacji painter.save() i .restore() zamiast obrotów -self.kat_dorotacji
#TODO: ukrywanie label e2 teraz jak jest QSCrollArea nie dziala, bo to sie dzieje na zewnatrz, pokazanie wszystkich widzetow


class DataEdit(QWidget):
    changeDiode = Signal(StatusDiodes.Status)
    
    def __init__(self, parent: AbstractTab, model) -> None:
        super().__init__(parent)
        self.model = model

        self.input_widgets = {
            "e1": DoubleSpinBox(self.model.input_dane["e1"], 0, 10, 0.05),
            "e2": DoubleSpinBox(self.model.input_dane["e2"], 0, 10, 0.05),
            "f_kt": DoubleSpinBox(self.model.input_dane["f_kt"], 0.00001, 0.0001, 0.00001, 5),
            "f_ts": DoubleSpinBox(self.model.input_dane["f_ts"], 0.00001, 0.0001, 0.00001, 5),
        }
        self.tuning_widgets = {
            "wsp_k": DoubleSpinBox(self.model.input_dane["wsp_k"], 1.2, 1.5, 0.05),
            "d_sw": DoubleSpinBox(self.model.input_dane["d_sw"], 5, step=0.1),
            "d_tul": DoubleSpinBox(self.model.input_dane["d_tul"], 5, step=0.1),
        }

        self.visual_frame = VisualsFrame(self, model)
        self.visual_frame.accepted.connect(self.visualsChanged)

        self.support_popup = SupportWin()
        self.support_popup.choiceMade.connect(self.closeChoiceWindow)
        self.ch_support_button = QPushButton(text="Wybierz sposób podparcia kół")
        self.ch_support_button.clicked.connect(self.support_popup.show)
        self.ch_var_label = QLabelD("")

        self.material_frame = MaterialsFrame(self, model)
        self.material_frame.updated.connect(self.inputsChanged)

        self.results_frame = ResultsFrame(self, model)
        self.label_e2 = QLabelD("Odstęp pomiędzy kołami")
        self.obl_srednice_labels = [QLabelD(style=False), QLabelD(style=False), QLabelD(style=False)]

        self.accept_button = QPushButton("Oblicz")
        self.accept_button.clicked.connect(lambda: self.recalculate())

        for key in self.tuning_widgets:
            self.tuning_widgets[key].valueChanged.connect(lambda: self.recalculate())
        for key in self.input_widgets:
            self.input_widgets[key].valueChanged.connect(self.inputsChanged)
        
        layout = QGridLayout()
        self.setupSmallLayout(layout)
        self.setLayout(layout)
        # self.visualsChanged(False)
    
    def inputsChanged(self):
        self.accept_button.setEnabled(True)
        for widget in self.tuning_widgets.values():
            widget.setEnabled(False)
        self.changeDiode.emit(StatusDiodes.Status.WARNING)
    
    def visualsChanged(self, is_accepted):
        for child in (child for child in self.children() if child != self.visual_frame):
            child.setEnabled(is_accepted)
    
    def setupLayout(self, layout: QGridLayout) -> None:
        # layout.setVerticalSpacing(10)
        # n_label = QLabelD("Liczba sworzni [n]")
        # layout.addWidget(n_label, 0, 0, 1, 2)
        # layout.addWidget(self.input_widgets["n"], 0, 2, 1, 2)
        # lab_Rwt = QLabelD("R<sub>wt</sub> [mm]")
        # lab_Rwt.setToolTip("Promień rozmieszczenia sworzni")
        # layout.addWidget(lab_Rwt, 1, 0)
        # layout.addWidget(self.input_widgets["R_wt"], 1, 1)
        # name_Rwk = QLabelD("R<sub>wk</sub>")
        # name_Rwk.setToolTip("Promień rozmieszczenia otworów w kole cykloidalnym")
        # layout.addWidget(name_Rwk, 1, 2)
        # layout.addWidget(self.Rwk_label, 1, 3)
        # TODO: moze byc za male
        layout.addWidget(self.visual_frame, 0, 0, 2, 4)
        layout.addWidget(self.material_frame, 0, 5, 6, 4)
        layout.addWidget(self.ch_support_button, 2, 0, 1, 2)
        layout.addWidget(self.ch_var_label, 2, 2, 1, 2)
        layout.addWidget(self.labels["e1"], 3, 0, 1, 3)
        layout.addWidget(self.input_widgets["e1"], 3, 3)
        layout.addWidget(self.label_e2, 4, 0, 1, 3)
        layout.addWidget(self.input_widgets["e2"], 4, 3)

        layout.addWidget(self.labels["f_header"], 6, 5, 1, 4)
        layout.addWidget(self.labels["f_kt"], 7, 5, 1, 3)
        layout.addWidget(self.input_widgets["f_kt"], 7, 8)
        layout.addWidget(self.labels["f_ts"], 8, 5, 1, 3)
        layout.addWidget(self.input_widgets["f_ts"], 8, 8)

        # spac = QSpacerItem(100, 100, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # layout.addItem(spac, 10, 0)
        # layout.addItem(spac, 0, 4)

        layout.addWidget(self.accept_button, 11, 3, 1, 3)
        self.accept_button.show()

        layout.addWidget(self.labels["dia_header"], 12, 0, 1, 4)
        layout.addWidget(self.labels["d_pin_calc"], 13, 0)
        layout.addWidget(self.labels["d_sleeve_calc"], 13, 1)
        
        layout.addWidget(self.obl_srednice_labels[0], 14, 0)
        layout.addWidget(self.obl_srednice_labels[1], 14, 1)
        layout.addWidget(self.labels["k"], 15, 0)
        layout.addWidget(self.tuning_widgets["wsp_k"], 15, 1)
        layout.addWidget(self.labels["dia_select_header"], 16, 0, 1, 4)
        layout.addWidget(self.labels["d_pin_select"], 17, 0)
        layout.addWidget(self.labels["d_sleeve_select"], 17, 1)
        layout.addWidget(self.labels["d_hole"], 17, 2)
        layout.addWidget(self.tuning_widgets["d_sw"], 18, 0)
        layout.addWidget(self.tuning_widgets["d_tul"], 18, 1)
        layout.addWidget(self.obl_srednice_labels[2], 18, 2)

        layout.addWidget(self.results_frame, 12, 6, 6, 3)
        self.results_frame.show()

    def setupSmallLayout(self, layout: QGridLayout) -> None:
        if not hasattr(self, "labels"):
            self.labels = {
                "e1": QLabelD("Odstęp pomiędzy kołem a tarczą"),
                "f_header": QLabelD("Współczynniki tarcia dla pary ciernej:", style=False),
                "f_kt": QLabelD("tuleja - koło cykloidalne"),
                "f_ts": QLabelD("sworzeń - tuleja"),
                "dia_header": QLabelD("Obliczone średnice:"),
                "d_pin_calc": QLabelD("sworznia - d<sub>s</sub>"),
                "d_sleeve_calc": QLabelD("tuleji - d<sub>t</sub>"),
                "k": QLabelD("k"),
                "dia_select_header": QLabelD("Dobierz średnice [mm]:"),
                "d_pin_select": QLabelD("sworznia - d<sub>s</sub>"),
                "d_sleeve_select": QLabelD("tuleji - d<sub>t</sub>"),
                "d_hole": QLabelD("otworów - d<sub>otw</sub>"),
            }
            self.labels["k"].setToolTip("Współczynnik grubości ścianki tuleji")
            # lab_f_kt.setToolTip("f kt - Współczynnik tarcia tocznego pomiędzy otworem w kole a tuleją")
            # lab_f_ts.setToolTip("f ts -Współczynnik tarcia tocznego pomiędzy tuleją a sworzniem")
        
        layout.addWidget(self.visual_frame, 0, 0, 2, 12)

        layout.addWidget(self.ch_support_button, 2, 0, 1, 6)
        layout.addWidget(self.ch_var_label, 2, 6, 1, 6)
        layout.addWidget(self.labels["e1"], 3, 0, 1, 6)
        layout.addWidget(self.input_widgets["e1"], 3, 6, 1, 6)
        layout.addWidget(self.label_e2, 4, 0, 1, 6)
        layout.addWidget(self.input_widgets["e2"], 4, 6, 1, 6)

        layout.addWidget(self.material_frame, 5, 0, 8, 12)

        layout.addWidget(self.labels["f_header"], 13, 0, 1, 12)
        layout.addWidget(self.labels["f_kt"], 14, 0, 1, 6)
        layout.addWidget(self.input_widgets["f_kt"], 14, 6, 1, 6)
        layout.addWidget(self.labels["f_ts"], 15, 0, 1, 6)
        layout.addWidget(self.input_widgets["f_ts"], 15, 6, 1, 6)

        layout.addWidget(self.accept_button, 16, 4, 1, 4)

        layout.addWidget(self.labels["dia_header"], 17, 0, 1, 12)
        layout.addWidget(self.labels["d_pin_calc"], 18, 0, 1, 4)
        layout.addWidget(self.labels["d_sleeve_calc"], 18, 4, 1, 4)
        
        layout.addWidget(self.obl_srednice_labels[0], 19, 0, 1, 4)
        layout.addWidget(self.obl_srednice_labels[1], 19, 4, 1, 4)
        layout.addWidget(self.labels["k"], 20, 0, 1, 6)
        layout.addWidget(self.tuning_widgets["wsp_k"], 20, 6, 1, 6)
        layout.addWidget(self.labels["dia_select_header"], 21, 0, 1, 12)
        layout.addWidget(self.labels["d_pin_select"], 22, 0, 1, 4)
        layout.addWidget(self.labels["d_sleeve_select"], 22, 4, 1, 4)
        layout.addWidget(self.labels["d_hole"], 22, 8, 1, 4)
        layout.addWidget(self.tuning_widgets["d_sw"], 23, 0, 1, 4)
        layout.addWidget(self.tuning_widgets["d_tul"], 23, 4, 1, 4)
        layout.addWidget(self.obl_srednice_labels[2], 23, 8, 1, 4)

        layout.addWidget(self.results_frame, 24, 0, 6, 12)

    def recalculate(self, angle: float=None) -> None:
        if angle:
            self.model.wheel_rotation_angle = angle
        if not self.model.module_enabled:
            return
        
        input_values = {key: self.input_widgets[key].value() for key in self.input_widgets}
        # this check happens before adding the values of tuning widgets, because those will only be filled out after the first time calculations are run,
        # and are not neccesary for calculations (except the sleeve_coef, which is prefilled).
        if any((value is None for value in input_values.values())): return
        if self.model.input_dane["podparcie"] is None: return

        input_values.update({key: self.tuning_widgets[key].value() for key in self.tuning_widgets})
        results = self.model.recalculate(input_values)

        self.obl_srednice_labels[0].setText(str(results["d_s_obl"]) + " mm")
        self.obl_srednice_labels[1].setText(str(results["d_t_obl"]) + " mm")
        self.obl_srednice_labels[2].setText(str(results["d_o_obl"]) + " mm")
        self.tuning_widgets["d_sw"].modify(minimum=results["d_s_obl"])
        self.tuning_widgets["d_tul"].modify(minimum=results["d_t_obl"])

        self.results_frame.update()
        self.accept_button.setEnabled(False)
        for widget in self.tuning_widgets.values():
            widget.setEnabled(True)

    # TODO: fix with new changes
    # def copyDataToInputs(self, new_input_data: Dict[str, Union[int, float]]) -> None:
    #     for key in self.input_widgets:
    #         self.input_widgets[key].blockSignals(True)
    #         self.input_widgets[key].setValue(new_input_data[key])
    #         self.input_widgets[key].blockSignals(False)
    #     self.recalculate()

    def closeChoiceWindow(self, choice: str) -> None:
        self.model.input_dane["podparcie"] = choice
        self.ch_var_label.setText(choice)
        self.support_popup.hide()
        self.changeDiode.emit(StatusDiodes.Status.WARNING)
        self.accept_button.setEnabled(True)

    def toleranceUpdate(self, tol_data: Optional[Dict[str, Union[float, Tuple[float, float]]]]) -> None:
        self.model.tol_data = tol_data
        self.recalculate()


class PinOutTab(AbstractTab):
    thisEnabled = Signal(bool)
    animDataUpdated = Signal(dict)
    errorsUpdated = Signal(dict)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.model = PinOutputMechanismModel()

        layout = QVBoxLayout()
        self.setLayout(layout)
        button_layout = QGridLayout()
        layout.addLayout(button_layout)

        self.diodes = StatusDiodes(self, ("Stan: Wystąpił błąd", "Stan: Niezaakceptowane zmiany w obliczeniach", "Stan: Mechanizm zaakceptowany", "Stan: Moduł nieużywany"))
        layout.addWidget(self.diodes)

        self.use_this_check = QCheckBox(text="Używaj tego mechanizmu wyjściowego")
        button_layout.addWidget(self.use_this_check, 1, 0, 1, 2)

        help_pdf_button = QPushButton("Pomoc")
        button_layout.addWidget(help_pdf_button, 1, 2)
        help_pdf_button.clicked.connect(lambda: open_pdf("resources//help_docs//mechanizmy-sworzniowe-help-1.pdf"))

        self.data = DataEdit(self, self.model)
        self.wykresy = ResultsTab(self, "numer sworznia", {
            "sily": {"repr_name": "Siły", "chart_title": "Siły na sworzniach", "y_axis_title": "Siła [N]"},
            "naciski": {"repr_name": "Naciski", "chart_title": "Naciski powierzchniowe na sworzniach", "y_axis_title": "Wartość Nacisku [MPa]"},
            "straty": {"repr_name": "Straty", "chart_title": "Straty mocy na sworzniach", "y_axis_title": "Straty mocy [W]"},
            "luzy": {"repr_name": "Luzy", "chart_title": "Luzy na sworzniach", "y_axis_title": "Luz [mm]"},
        })
        self.tol_edit = ToleranceEdit(self, (
            ("T_o", "T<sub>o</sub>", "Tolerancja wykonania promieni otworów w kole cykloidalnym"),
            ("T_t", "T<sub>t</sub>", "Tolerancja wykonania promieni tuleji"),
            ("T_s", "T<sub>s</sub>", "Tolerancja wykonania promieni sworzni"),
            ("T_Rk", "T<sub>Rk</sub>", "Tolerancja wykonania promienia rozmieszczenia otworów w kole cykloidalnym"),
            ("T_Rt", "T<sub>Rt</sub>", "Tolerancja wykonania promienia rozmieszczenia tulei w elemencie wyjściowym"),
            ("T_fi_k", "T<sub>\u03c6k</sub>", "Tolerancja wykonania kątowego rozmieszczenia otworów w kole cykloidalnym"),
            ("T_fi_t", "T<sub>\u03c6t</sub>", "Tolerancja wykonania kątowego rozmieszczenia tulei w elemencie wyjściowym"),
            ("T_e", "T<sub>e</sub>", "Tolerancja wykonania mimośrodu"),
        ))
        
        scrollable_tab = ResponsiveContainer(self, self.data, self.data.setupSmallLayout, self.data.setupLayout, 620, 1200)
        tab_titles = ["Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        stacked_widgets = [scrollable_tab, self.wykresy, self.tol_edit]

        stacklayout = QStackedLayout()
        layout.addLayout(stacklayout)

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button, 0, index)
            stacklayout.addWidget(widget)
            button.pressed.connect(partial(stacklayout.setCurrentIndex, index))

        self.model.animDataUpdated.connect(self.animDataUpdated.emit)
        self.model.errorsUpdated.connect(self.errorsUpdated.emit)
        self.model.shouldSendData.connect(self.sendData)
        self.model.chartDataUpdated.connect(self.wykresy.updateResults)
        self.model.changeDiode.connect(self.diodes.enableDiode)
        self.data.changeDiode.connect(self.diodes.enableDiode)
        self.tol_edit.toleranceDataUpdated.connect(self.data.toleranceUpdate)
        self.use_this_check.stateChanged.connect(self.useThisChanged)

        self.data.setEnabled(False)
        self.tol_edit.setEnabled(False)
    
    def useThisChanged(self, state: bool) -> None:
        '''
        Method run when the module is enabled through the check box at the top.
        The check box allows the user to pick the desired output mechanism, as the program foresees multiple of them,
        each in a seperate module.
        '''
        self.data.setEnabled(state)
        self.tol_edit.setEnabled(state)
        if state:
            self.thisEnabled.emit(True)
            self.model.module_enabled = True
            self.data.recalculate()
            if not self.data.visual_frame.filled_out or not self.data.visual_frame.is_accepted:
                self.data.visualsChanged(False)
            if self.model.has_error == True:
                self.diodes.enableDiode(StatusDiodes.Status.ERROR)
            elif self.data.accept_button.isEnabled() or not self.data.visual_frame.filled_out:
                self.diodes.enableDiode(StatusDiodes.Status.WARNING)
            else:
                self.diodes.enableDiode(StatusDiodes.Status.OK)
        else:
            self.thisEnabled.emit(False)
            self.model.module_enabled = False
            self.diodes.enableDiode(StatusDiodes.Status.DISABLED)
            self.animDataUpdated.emit({"PinOutTab": False})

    def useOtherChanged(self, state: bool) -> None:
        '''
        This method is run when another output mechanism module signals a change in its module enabling check box.
        It ensures that only one output mechanism module is used.
        '''
        self.use_this_check.setEnabled(not state)

    def sendData(self) -> None:
        self.dataChanged.emit({"PinOutTab": {
            "Fwm": self.model.obliczone_dane["F_wmr"],
            "r_mr": self.model.obliczone_dane["r_mr"],
            "x": self.model.input_dane["e2"],
        }})
    
    def receiveData(self, new_data) -> None:
        wanted_data = None
        if new_data.get("GearTab") is not None:
            wanted_data = new_data.get("GearTab")
        elif new_data.get("base") is not None:
            wanted_data = new_data.get("base")
        else:
            return
        
        for key in wanted_data:
            if self.model.zew_dane.get(key) is not None:
                self.model.zew_dane[key] = wanted_data[key]

        # if wanted_data.get("K") == 2:
        #     self.data.label_e2.show()
        #     self.data.input_widgets["e2"].show()
        # elif wanted_data.get("K") == 1:
        #     self.data.label_e2.hide()
        #     self.data.input_widgets["e2"].hide()
        if not self.model.module_enabled:
            return

        if self.diodes.current_status == StatusDiodes.Status.WARNING:
            self.model.sendAnimationUpdates(self.model.input_dane["n"], self.model.input_dane["R_wt"])
        elif self.diodes.current_status == StatusDiodes.Status.OK:
            self.data.recalculate()

    # TODO: update save & loading, report csv etc.
    def saveData(self) -> Dict:
        # self.data.recalculate()
        return {
            "input_dane": self.data.input_dane,
            "zew_dane": self.data.zew_dane,
            "material_data": self.model.material_data,
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
        materials = self.model.material_data
        wyniki = obliczenia_mech_wyjsciowy(self.model.input_dane, self.model.zew_dane, materials, self.model.tol_data, self.model.wheel_rotation_angle)

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
            text += a + borders + "\\cellx4000" + borders + "\\cellx4800" + borders + "\\cellx5600" + borders + "\\cellx6400" + start + str(index) + end + start + "{:.1f}".format(row[0]) + end + start + "{:.2f}".format(row[1]) + end + start + "{:.3f}".format(row[2]) + end + endrow

        text += "\\line"
        return text

    def csvData(self) -> str:
        if not self.model.module_enabled:
            return ''
        wyniki = obliczenia_mech_wyjsciowy(self.model.input_dane, self.model.zew_dane, self.model.material_data, self.model.tol_data, self.model.wheel_rotation_angle)
        title = "Mechanizm wyjściowy ze sworzniami\n"
        sily_text = [f"{i},{round(wyniki['sily'][0][i], 1)}\n" for i in range(1, len(wyniki['sily']) + 1)]
        naciski_text = [f"{i},{round(wyniki['naciski'][0][i], 2)}\n" for i in range(1, len(wyniki['naciski']) + 1)]
        straty_text = [f"{i},{round(wyniki['straty'][0][i], 3)}\n" for i in range(1, len(wyniki['straty']) + 1)]
        return title + "Siły na sworzniach [N]\n".join(sily_text) + "Naciski powierzchniowe na sworzniach [MPa]\n".join(naciski_text) + "Straty mocy na sworzniach [W]\n".join(straty_text) + "\n"
