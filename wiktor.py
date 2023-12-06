from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QComboBox, QStackedLayout, QCheckBox, QButtonGroup
from PySide2.QtCore import Signal, QSize, Qt
from PySide2.QtGui import QIcon, QPixmap
from Mech_wyj_tuleje.tuleje_obl import obliczenia_mech_wyjsciowy
from Mech_wyj_tuleje.wykresy import ChartTab
from functools import partial
from abstract_tab import AbstractTab
from Mech_wyj_tuleje.utils import sprawdz_przecinanie_otworow
from common_widgets import DoubleSpinBox, QLabelD, IntSpinBox
from math import pi

#TODO: mam przesunięte do tyłu w poziomie punkty wykresów. Pawel też.
# moze jakos usuwac dane z wykresow jak sa bledy?

class PopupWin(QWidget):
    choice_made = Signal(str)
    VARIANTS = [
        "jednostronnie utwierdzony",
        "utwierdzony podparty",
        "obustronnie utwierdzony",
    ]
    VARIANTS_V = [
        "Sworzeń zamocowany jednostronnie w tarczy elementu wyjściowego",
        "Sworzeń podparty i z drugiej strony zamocowany w tarczy śrubami luźno pasowanymi",
        "Sworzeń podparty i z drugiej strony zamocowany w tarczy śrubami ciasno pasowanymi",
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wybór sposobu mocowania sworzni")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(1300, 500)

        layout = QGridLayout()
        self.buttons = [
            QPushButton(icon=QIcon("icons//sworzen_jednostronnie_utwierdzony.png")),
            QPushButton(icon=QIcon("icons//sworzen_utwierdzony_podparty.png")),
            QPushButton(icon=QIcon("icons//sworzen_obustronnie_utwierdzony.png"))
        ]
        for ind, button in enumerate(self.buttons):
            button.setIconSize(QSize(400, 400))
            button.clicked.connect(partial(self.choice_made.emit, self.VARIANTS[ind]))
            layout.addWidget(button, 0, ind, 9, 1)
            layout.addWidget(QLabelD(self.VARIANTS_V[ind]), 10, ind, 1, 1)
        self.setLayout(layout)


class DataEdit(QWidget):
    wykresy_data_updated = Signal(dict)
    anim_data_updated = Signal(dict)
    errors_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.kat_obrotu_kola = 0
        self.tol_data = {"tolerances": None}
        self.input_dane = {
            "M_k": 500,
            "n": 10,
            "R_wk": 80,
            "mat_sw": {"nazwa": "17Cr3", "E": 210000, "v": 0.3, "k_g": 300},
            "mat_tul": {"nazwa": "17Cr3", "E": 210000, "v": 0.3, "k_g": 300},
            "b": 25,
            "podparcie": "jednostronnie utwierdzony",
            "d_sw": 5,
            "d_tul": 7,
            "wsp_k": 1.2,
            "e1": 1,
            "e2": 1,
            "f_kt": 0.00005,
            "f_ts": 0.00005,
        }
        self.obliczone_dane = {
            "d_sw": 10,
            "d_tul": 14,
            "d_otw": 20
        }
        self.zew_dane = {
            "R_w1": 72,
            "R_f1": 107,
            "e": 3,
            "M": 500,
            "K": 2,
            "n_wej": 500,
            "E_kola": 210000,
            "v_kola": 0.3,
        }
        # TODO: ostatecznie brac z bazy danych
        self.materialy = [
            {"nazwa": "17Cr3", "E": 210000, "v": 0.3, "k_g": 300},
            {"nazwa": "20MnCr5", "E": 210000, "v": 0.3, "k_g": 450},
            {"nazwa": "C45", "E": 210000, "v": 0.3, "k_g": 205},
            {"nazwa": "test", "E": 210000, "v": 0.3, "k_g": 325},
        ]

        # TODO: zmienic dokladnie te min i maxy
        self.input_widgets = {
            "n": IntSpinBox(self.input_dane["n"], 4, 20, 1),
            "R_wk": DoubleSpinBox(self.input_dane["R_wk"], 40, 200, 1, 1),
            "mat_sw": QComboBox(),
            "mat_tul": QComboBox(),
            "b": DoubleSpinBox(self.input_dane["b"], 5, 30, 0.1),
            "e1": DoubleSpinBox(self.input_dane["e1"], 0, 10, 0.05),
            "e2": DoubleSpinBox(self.input_dane["e2"], 0, 10, 0.05),
            "wsp_k": DoubleSpinBox(1.3, 1.2, 1.5, 0.05),
            "d_sw": DoubleSpinBox(6, 5, 14, 0.1),
            "d_tul": DoubleSpinBox(6, 5, 14, 0.1),
            "f_kt": DoubleSpinBox(self.input_dane["f_kt"], 0.00001, 0.0001, 0.00001, 5),
            "f_ts": DoubleSpinBox(self.input_dane["f_ts"], 0.00001, 0.0001, 0.00001, 5),
        }
        self.input_widgets["mat_sw"].addItems([mat["nazwa"] for mat in self.materialy])
        self.input_widgets["mat_tul"].addItems([mat["nazwa"] for mat in self.materialy])

        self.popup = PopupWin()
        self.popup.choice_made.connect(self.close_choice_window)
        self.ch_var_button = QPushButton(text="Wybierz sposób podparcia kół")
        self.ch_var_button.clicked.connect(self.popup.show)
        self.ch_var_label = QLabelD("jednostronnie utwierdzony")

        self.label_e2 = QLabelD("Przerwa między kołami")
        self.obl_srednice_labels = [QLabel(), QLabel(), QLabel()]

        for widget in self.input_widgets.values():
            if type(widget) == QComboBox:
                widget.currentIndexChanged.connect(lambda: self.inputs_modified(self.kat_obrotu_kola))
            elif type(widget) == DoubleSpinBox or IntSpinBox:
                widget.valueChanged.connect(lambda: self.inputs_modified(self.kat_obrotu_kola))
        
        self.setup_layout()
        self.inputs_modified(self.kat_obrotu_kola)
        
        self.input_widgets["e2"].hide()
        self.label_e2.hide()
    
    def setup_layout(self):
        layout = QGridLayout()
        layout1 = QGridLayout()

        layout.addWidget(QLabelD("Ilość sworzni [n]"), 0, 0)
        layout.addWidget(self.input_widgets["n"], 0, 1)
        layout.addWidget(QLabelD("Promień rozstawu sworzni [R<sub>wk</sub>]"), 1, 0)
        layout.addWidget(self.input_widgets["R_wk"], 1, 1)
        layout.addWidget(QLabelD("Materiał sworznia"), 2, 0)
        layout.addWidget(self.input_widgets["mat_sw"], 2, 1)
        layout.addWidget(QLabelD("Materiał tuleji"), 3, 0)
        layout.addWidget(self.input_widgets["mat_tul"], 3, 1)
        lab_b = QLabelD("b")
        lab_b.setToolTip("Grubość koła cykloidalnego")
        layout.addWidget(lab_b, 4, 0)
        layout.addWidget(self.input_widgets["b"], 4, 1)

        lab_f_kt = QLabelD("f<sub>kt</sub>")
        lab_f_kt.setToolTip("f kt - Współczynnik tarcia tocznego pomiędzy otworem w kole a tuleją")
        layout.addWidget(lab_f_kt, 5, 0)
        layout.addWidget(self.input_widgets["f_kt"], 5, 1)
        lab_f_ts = QLabelD("f<sub>ts</sub>")
        lab_f_ts.setToolTip("f ts -Współczynnik tarcia tocznego pomiędzy tuleją a sworzniem")
        layout.addWidget(lab_f_ts, 6, 0)
        layout.addWidget(self.input_widgets["f_ts"], 6, 1)

        layout.addWidget(self.ch_var_button, 7, 0)
        layout.addWidget(self.ch_var_label, 7, 1)

        layout.addWidget(QLabelD("Przerwa między kołem a tarczą"), 8, 0)
        layout.addWidget(self.input_widgets["e1"], 8, 1)
        layout.addWidget(self.label_e2, 9, 0)
        layout.addWidget(self.input_widgets["e2"], 9, 1)

        layout1.addWidget(QLabelD("Obliczone średnice:"), 0, 0, 1, 3)
        layout1.addWidget(QLabelD("sworznia"), 1, 0)
        layout1.addWidget(QLabelD("tuleji"), 1, 1)
        layout1.addWidget(QLabelD("otworów"), 1, 2)
        
        layout1.addWidget(self.obl_srednice_labels[0], 2, 0)
        layout1.addWidget(self.obl_srednice_labels[1], 2, 1)
        layout1.addWidget(self.obl_srednice_labels[2], 2, 2)
        lab_k = QLabelD("k")
        lab_k.setToolTip("Współczynnik grubości ścianki tuleji")
        layout1.addWidget(lab_k, 3, 0)
        layout1.addWidget(self.input_widgets["wsp_k"], 3, 1)
        layout1.addWidget(QLabelD("Dobierz średnice:"), 4, 0, 1, 3)
        layout1.addWidget(QLabelD("sworznia"), 5, 0)
        layout1.addWidget(QLabelD("tuleji"), 5, 1)
        layout1.addWidget(self.input_widgets["d_sw"], 6, 0)
        layout1.addWidget(self.input_widgets["d_tul"], 6, 1)

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout)
        layout_main.addLayout(layout1)
        self.setLayout(layout_main)

    def inputs_modified(self, kat, update=True):
        self.kat_obrotu_kola = kat
        if not update or not self.parent().use_this_check.isChecked():
            return
        
        for key, widget in self.input_widgets.items():
            if type(widget) == QComboBox:
                self.input_dane[key] = self.materialy[self.input_widgets[key].currentIndex()]
            elif type(widget) == DoubleSpinBox or IntSpinBox:
                self.input_dane[key] = self.input_widgets[key].value()

        wyniki = obliczenia_mech_wyjsciowy(self.input_dane, self.zew_dane, self.tol_data, self.kat_obrotu_kola)

        self.obliczone_dane["d_sw"] = wyniki["d_s_obl"]
        self.obliczone_dane["d_tul"] = wyniki["d_t_obl"]
        self.obliczone_dane["d_otw"] = wyniki["d_o_obl"]
        self.obl_srednice_labels[0].setText(str(wyniki["d_s_obl"]))
        self.obl_srednice_labels[1].setText(str(wyniki["d_t_obl"]))
        self.obl_srednice_labels[2].setText(str(wyniki["d_o_obl"]))
        self.input_widgets["d_sw"].modify(minimum=wyniki["d_s_obl"], maximum=wyniki["d_t_obl"])
        self.input_dane["d_sw"] = self.input_widgets["d_sw"].value()
        self.input_widgets["d_tul"].modify(minimum=wyniki["d_t_obl"], maximum=wyniki["d_o_obl"])
        self.input_dane["d_tul"] = self.input_widgets["d_tul"].value()

        anim_data = {
            "n": self.input_dane["n"],
            "R_wk": self.input_dane["R_wk"],
            "d_sw": self.input_dane["d_sw"],
            "d_tul": self.input_dane["d_tul"],
            "d_otw": self.obliczone_dane["d_otw"],
        }
        if anim_data["R_wk"] + anim_data["d_otw"] / 2 >= self.zew_dane["R_f1"]:
            self.anim_data_updated.emit({"wiktor": None})
            self.errors_updated.emit({"R_wk duze": True})
        elif sprawdz_przecinanie_otworow(self.input_dane["R_wk"], self.input_dane["n"], self.obliczone_dane["d_otw"]):
            self.anim_data_updated.emit({"wiktor": None})
            self.errors_updated.emit({"R_wk male": True})
        else:
            self.errors_updated.emit({"R_wk duze": False, "R_wk male": False})
            self.anim_data_updated.emit({"wiktor": anim_data})
            self.wykresy_data_updated.emit({
            "sily": wyniki["sily"],
            "naciski": wyniki['naciski'],
            "straty": wyniki['straty'],
            })
    
    def copyDataToInputs(self, new_input_data):
        for key, widget in self.input_widgets.items():
            if type(widget) == QComboBox:
                loaded_index = self.materialy.index(new_input_data[key])
                self.input_widgets[key].setCurrentIndex(loaded_index)
            elif type(widget) == DoubleSpinBox or IntSpinBox:
                self.input_widgets[key].setValue(new_input_data[key])
        self.input_dane = new_input_data

    def close_choice_window(self, choice):
        self.input_dane["podparcie"] = choice
        self.ch_var_label.setText(choice)
        self.popup.hide()
        self.inputs_modified(self.kat_obrotu_kola)

    def tolerance_update(self, tol_data):
        self.tol_data = tol_data
        self.inputs_modified(self.kat_obrotu_kola)


class ToleranceInput(QWidget):
    def __init__(self, parent, label_text, tooltip_text):
        super().__init__(parent)
        self.tol = [0, 0, 0]

        self.label = QLabelD(label_text)
        self.label.setToolTip(tooltip_text)
        self.low_input = DoubleSpinBox(self.tol[0], -0.05, 0.05, 0.001, 3)
        self.high_input = DoubleSpinBox(self.tol[1], -0.05, 0.05, 0.001, 3)
        self.deviation_input = DoubleSpinBox(self.tol[2], -0.05, 0.05, 0.001, 3)

        self.low_input.valueChanged.connect(self.modified_low)
        self.high_input.valueChanged.connect(self.modified_high)
        self.deviation_input.valueChanged.connect(self.modified_deviation)

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.low_input, 0, 1)
        layout.addWidget(self.high_input, 0, 2)
        layout.addWidget(self.deviation_input, 0, 3)
        self.setLayout(layout)
    
    def setEnabled(self, arg__1: bool) -> None:
        super().setEnabled(arg__1)
        self.label.setEnabled(arg__1)
        self.low_input.setEnabled(arg__1)
        self.high_input.setEnabled(arg__1)
        self.deviation_input.setEnabled(arg__1)

    def modified_low(self):
        self.tol[0] = round(self.low_input.value(), 3)
        self.high_input.modify(minimum=self.tol[0])
        # self.low_input.modify(maximum=self.tol[1])
    
    def modified_high(self):
        self.tol[1] = round(self.high_input.value(), 3)
        self.low_input.modify(maximum=self.tol[1])
        # self.high_input.modify(minimum=self.tol[0])
    
    def modified_deviation(self):
        self.tol[2] = round(self.deviation_input.value(), 3)
    
    def change_mode(self, mode):
        if mode == "deviations":
            self.low_input.hide()
            self.high_input.hide()
            self.deviation_input.show()
        else:
            self.low_input.show()
            self.high_input.show()
            self.deviation_input.hide()


class ToleranceEdit(QWidget):
    tolerance_data_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        self.fields = {
            "T_o": ToleranceInput(self, "T_o", "Tolerancja wykonania promieni otworów w kole cykloidalnym"),
            "T_t": ToleranceInput(self, "T_t", "Tolerancja wykonania promieni tuleji"),
            "T_s": ToleranceInput(self, "T_s", "Tolerancja wykonania promieni sworzni"),
            "T_Rk": ToleranceInput(self, "T_Rk", "Tolerancja wykonania promienia rozmieszczenia otworów w kole cykloidalnym"),
            "T_Rt": ToleranceInput(self, "T_Rt", "Tolerancja wykonania promienia rozmieszczenia tulei w elemencie wyjściowym"),
            "T_fi_k": ToleranceInput(self, "T_fi_k", "Tolerancja wykonania kątowego rozmieszczenia otworów w kole cykloidalnym"),
            "T_fi_t": ToleranceInput(self, "T_fi_t", "Tolerancja wykonania kątowego rozmieszczenia tulei w elemencie wyjściowym"),
            "T_e": ToleranceInput(self, "T_e", "Tolerancja wykonania mimośrodu"),
        }
        self.labels = { key: [QLabelD(key), QLabelD("0"), QLabelD("0"), QLabelD("0")] for key in self.fields }
        self.tolerancje = { key: widget.tol for key, widget in self.fields.items() }
        self.mode = "deviations"
        self.check = QCheckBox(text="Używaj luzów w obliczeniach")
        self.check.stateChanged.connect(self.on_check)

        self.label_top = QLabelD("Ustaw odchyłkę:")
        self.label_bottom = QLabelD("Obecne odchyłki:")

        self.tol_check = QCheckBox(text="Wybierz pole tolerancji")
        #TODO: odblokowac po ustaleniu sposobu obliczen
        self.tol_check.setEnabled(False)
        self.dev_check = QCheckBox(text="Wybierz odchyłkę")
        self.check_group = QButtonGroup(self)
        self.check_group.addButton(self.tol_check)
        self.check_group.addButton(self.dev_check)
        self.dev_check.stateChanged.connect(self.mode_changed)
        self.dev_check.setChecked(True)
        self.tol_check.setEnabled(False)
        self.dev_check.setEnabled(False)

        self.accept_button = QPushButton(text="Ustaw tolerancje")
        self.accept_button.clicked.connect(self.data_updated)
        self.accept_button.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.check, 0, 0)
        layout.addWidget(self.tol_check, 1, 0)
        layout.addWidget(self.dev_check, 1, 1)
        layout.addWidget(self.label_top, 2, 0, 1, 3)
        for ind, widget in enumerate(self.fields.values()):
            layout.addWidget(widget.label, 3+ind-ind%2, 0 + ind%2 * 3)
            layout.addWidget(widget.low_input, 3+ind-ind%2, 1 + ind%2 * 3)
            layout.addWidget(widget.high_input, 3+ind-ind%2, 2 + ind%2 * 3)
            layout.addWidget(widget.deviation_input, 3+ind-ind%2, 1 + ind%2 * 3)
            widget.setEnabled(False)
            widget.low_input.setEnabled(False)
            widget.high_input.setEnabled(False)
            widget.deviation_input.setEnabled(False)
        layout.addWidget(self.label_bottom, 11, 0, 1, 2)
        for ind, (l1, l2, l3, l4) in enumerate(self.labels.values()):
            layout.addWidget(l1, 12+ind-ind%2, 0 + ind%2 * 3)
            layout.addWidget(l2, 12+ind-ind%2, 1 + ind%2 * 3)
            layout.addWidget(l3, 12+ind-ind%2, 2 + ind%2 * 3)
            layout.addWidget(l4, 12+ind-ind%2, 1 + ind%2 * 3)
            l2.hide()
            l3.hide()
        layout.addWidget(self.accept_button)

        self.setLayout(layout)
        
    def on_check(self, state):
        enable = False if state == 0 else True
        self.accept_button.setEnabled(enable)
        #TODO: odblokowac po ustaleniu sposobu obliczen
        # self.tol_check.setEnabled(enable)
        self.dev_check.setEnabled(enable)
        self.label_top.setEnabled(enable)
        for widget in self.fields.values():
            widget.setEnabled(enable)
            widget.low_input.setEnabled(enable)
            widget.high_input.setEnabled(enable)
            widget.deviation_input.setEnabled(enable)
            self.accept_button.setEnabled(enable)
        if enable:
            self.data_updated()
        else:
            self.tolerance_data_updated.emit({"tolerances": None})
            for (_, l2, l3, l4) in self.labels.values():
                l2.setText("0")
                l3.setText("0")
                l4.setText("0")
    
    def mode_changed(self, state):
        mode = "deviations" if state == 2 else "tolerances"
        self.mode = mode
        for widget in self.fields.values():
            widget.change_mode(mode)
        if mode == "deviations":
            self.label_top.setText("Ustaw odchyłkę:")
            self.label_bottom.setText("Obecne odchyłki:")
            for (_, l2, l3, l4) in self.labels.values():
                l2.hide()
                l3.hide()
                l4.show()
        elif mode == "tolerances":
            self.label_top.setText("Ustaw pole tolerancji:")
            self.label_bottom.setText("Obecne tolerancje:")
            for (_, l2, l3, l4) in self.labels.values():
                l2.show()
                l3.show()
                l4.hide()

    def data_updated(self):
        for key, widget in self.fields.items():
            for ind in range(3):
                temp_text = str(widget.tol[ind]) if widget.tol[ind] <= 0 else "+" + str(widget.tol[ind])
                self.labels[key][ind+1].setText(temp_text)
        self.tolerance_data_updated.emit({"tolerances": {key: val[2] if self.mode == "deviations" else [val[0], val[1]] for key, val in self.tolerancje.items()}})
    
    def copyDataToInputs(self, new_tolerances):
        for key, widget in self.fields.items():
            widget.low_input.setValue(new_tolerances[key][0])
            widget.high_input.setValue(new_tolerances[key][1])
            widget.deviation_input.setValue(new_tolerances[key][2])


class TabWiktor(AbstractTab):
    this_enabled = Signal(bool)
    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout()
        button_layout = QGridLayout()
        stacklayout = QStackedLayout()
        layout.addLayout(button_layout)
        layout.addLayout(stacklayout)
        self.use_this_check = QCheckBox(text="Używaj tego mechanizmu wyjściowego")
        self.use_this_check.stateChanged.connect(self.useThisChanged)
        button_layout.addWidget(self.use_this_check, 1, 0, 1, 3)

        self.data = DataEdit(self)
        self.wykresy = ChartTab()
        self.tol_edit = ToleranceEdit(self)
        help_img = QLabel()
        pixmap = QPixmap("icons//pomoc_mechanizm_I.png").scaledToWidth(650)
        help_img.setPixmap(pixmap)
        self.data.wykresy_data_updated.connect(self.wykresy.updateCharts)
        self.tol_edit.tolerance_data_updated.connect(self.data.tolerance_update)

        tab_titles = ["Pomoc", "Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        stacked_widgets = [help_img, self.data, self.wykresy, self.tol_edit]

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button, 0, index)
            stacklayout.addWidget(widget)
            button.pressed.connect(partial(stacklayout.setCurrentIndex, index))

        self.setLayout(layout)
        self.data.setEnabled(False)
        self.tol_edit.setEnabled(False)
    
    def useThisChanged(self, state):
        self.data.setEnabled(state)
        self.tol_edit.setEnabled(state)
        if state:
            self.this_enabled.emit(True)
            self.data.inputs_modified(self.data.kat_obrotu_kola)
        else:
            self.this_enabled.emit(False)
            self.data.anim_data_updated.emit({"wiktor": None})

    def useOtherChanged(self, state):
        self.use_this_check.setEnabled(not state)

    def sendData(self):
        M_k = self.data.zew_dane["M"] / self.data.zew_dane["K"]
        R_wt = self.data.input_dane["R_wk"]
        return {
            "F_wm": 1000 * 4 * M_k/ (pi * R_wt),
            "r_m": pi * R_wt / 4,
        }
    
    def receiveData(self, new_data):
        if new_data is None:
            return
        dane_pawla = new_data.get("pawel")
        if dane_pawla is None:
            return
        for key in dane_pawla:
            if self.data.zew_dane.get(key) is not None:
                self.data.zew_dane[key] = dane_pawla[key]

        if dane_pawla.get("K") == 2:
            self.data.label_e2.show()
            self.data.input_widgets["e2"].show()
        elif dane_pawla.get("K") == 1:
            self.data.label_e2.hide()
            self.data.input_widgets["e2"].hide()
        if self.use_this_check.isChecked():
            self.data.inputs_modified(self.data.kat_obrotu_kola)

    def saveData(self):
        self.data.inputs_modified(self.data.kat_obrotu_kola)
        return {
            "input_dane": self.data.input_dane,
            "zew_dane": self.data.zew_dane,
            "tolerancje": self.tol_edit.tolerancje,
            "tol_mode": self.tol_edit.mode,
            "use_tol": self.tol_edit.check.isChecked()
        }

    def loadData(self, new_data):
        if new_data is None:
            return
        self.tol_edit.copyDataToInputs(new_data.get("tolerancje"))
        if new_data.get("tol_mode") == "deviations":
            self.tol_edit.tol_check.setChecked(False)
            self.tol_edit.dev_check.setChecked(True)
        else:
            self.tol_edit.tol_check.setChecked(True)
            self.tol_edit.dev_check.setChecked(False)
        self.tol_edit.check.setChecked(new_data.get("use_tol"))

        self.data.zew_dane = new_data.get("zew_dane")
        self.data.copyDataToInputs(new_data.get("input_dane"))

    def reportData(self):
        def table_row(cell1, cell2, cell3):
            a = "{\\trowd \\trgaph10 \\cellx5000 \\cellx7000 \\cellx8000 \\pard\\intbl "
            b = "\\cell\\pard\\intbl "
            return a + str(cell1) + b + str(cell2) + b + str(cell3) + " \\cell\\row}"

        if not self.use_this_check.isChecked():
            return ''
        wyniki = obliczenia_mech_wyjsciowy(self.data.input_dane, self.data.zew_dane, self.data.tol_data, self.data.kat_obrotu_kola)

        text = "{\\pard\\qc\\f0\\fs44 Mechanizm wyjściowy ze sworzniami\\line\\par}"
        text += table_row("Sposób podparcia", self.data.input_dane['podparcie'], "")
        text += table_row("Liczba otworów", self.data.input_dane['n'], "")
        text += table_row("Średnica otworu", self.data.obliczone_dane['d_otw'], "mm")
        text += table_row("Średnica rozmieszczenia otworów", self.data.input_dane['R_wk'], "mm")

        text += "{\\pard\\sb400\\sa100\\fs28 Tuleja: \\par}"
        text += table_row("Średnica zewnętrzna", self.data.input_dane['d_tul'], "mm")
        text += table_row("Średnica wewnętrzna", self.data.input_dane['d_sw'], "mm")
        text += table_row("Długość", self.data.input_dane['b'] * 2 + self.data.input_dane['e1'] * 2 + self.data.input_dane['e2'], "mm")
        text += table_row("Liczba", self.data.input_dane['n'], "")
        text += table_row("Materiał", self.data.input_dane['mat_tul']['nazwa'], "")
        text += table_row("E", self.data.input_dane['mat_tul']['E'], "MPa")
        text += table_row("v", self.data.input_dane['mat_tul']['v'], "")

        text += "{\\pard\\sb400\\sa100\\fs28 Sworzeń: \\par}"
        text += table_row("Średnica", self.data.input_dane['d_sw'], "mm")
        text += table_row("Długość", self.data.input_dane['b'] * 2 + self.data.input_dane['e1'] * 2 + self.data.input_dane['e2'], "mm")
        text += table_row("Liczba", self.data.input_dane['n'], "")
        text += table_row("Materiał", self.data.input_dane['mat_sw']['nazwa'], "")
        text += table_row("E", self.data.input_dane['mat_sw']['E'], "MPa")
        text += table_row("v", self.data.input_dane['mat_sw']['v'], "")

        text += table_row("f{\sub kt}", self.data.input_dane['f_kt'], "")
        text += table_row("f{\sub ts}", self.data.input_dane['f_ts'], "")

        text += table_row("Maksymalny nacisk powierzchniowy", max(wyniki['naciski'][0]), "MPa")
        text += table_row("Suma strat mocy", sum(wyniki['straty'][0]), "W")
        text += "\\line"
        return text

    def csvData(self):
        if not self.use_this_check.isChecked():
            return ''
        wyniki = obliczenia_mech_wyjsciowy(self.data.input_dane, self.data.zew_dane, self.data.tol_data, self.data.kat_obrotu_kola)
        title = "Mechanizm wyjściowy ze sworzniami\n"
        sily_text = [f"{i},{wyniki['sily'][0][i]}\n" for i in range(1, len(wyniki['sily']) + 1)]
        naciski_text = [f"{i},{wyniki['naciski'][0][i]}\n" for i in range(1, len(wyniki['naciski']) + 1)]
        straty_text = [f"{i},{wyniki['straty'][0][i]}\n" for i in range(1, len(wyniki['straty']) + 1)]
        return title + "Siły na sworzniach [N]\n".join(sily_text) + "Naciski powierzchniowe na sworzniach [MPa]\n".join(naciski_text) + "Straty mocy na sworzniach [W]\n".join(straty_text) + "\n"
