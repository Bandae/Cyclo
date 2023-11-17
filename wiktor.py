from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QStackedLayout, QCheckBox, QButtonGroup, QSizePolicy
from PySide2.QtCore import Signal, QSize, Qt
from PySide2.QtGui import QIcon
from Mech_wyj_tuleje.tuleje_obl import obliczenia_mech_wyjsciowy
from Mech_wyj_tuleje.wykresy import ChartTab
from functools import partial
from abstract_tab import AbstractTab
from Mech_wyj_tuleje.utils import sprawdz_przecinanie_otworow
from common_widgets import DoubleSpinBox, QLabelD, IntSpinBox

#TODO: mam przesunięte do tyłu w poziomie punkty wykresów

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

    def __init__(self, parent):
        super().__init__(parent)
        self.tol_data = {"tolerances": None}
        self.input_dane = {
            "M_k": 500,
            "n": 10,
            "R_wk": 80,
            "mat_sw": {"E": 210000, "v": 0.3, "k_g": 300},
            "mat_tul": {"E": 210000, "v": 0.3, "k_g": 300},
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
            "E_kola": 210000,
            "v_kola": 0.3,
        }
        # TODO: ostatecznie brac z bazy danych
        self.materialy = {
            "17Cr3": {"E": 210000, "v": 0.3, "k_g": 300},
            "20MnCr5": {"E": 210000, "v": 0.3, "k_g": 450},
            "C45": {"E": 210000, "v": 0.3, "k_g": 205},
            "test": {"E": 210000, "v": 0.3, "k_g": 325},
        }

        # TODO: zmienic dokladnie te min i maxy
        self.input_widgets = {
            "n_sw": IntSpinBox(self.input_dane["n"], 4, 16, 2),
            "R_wk": DoubleSpinBox(self.input_dane["R_wk"], 40, 200, 1),
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
        self.input_widgets["mat_sw"].addItems([mat for mat in self.materialy])
        self.input_widgets["mat_tul"].addItems([mat for mat in self.materialy])

        self.popup = PopupWin()
        self.popup.choice_made.connect(self.close_choice_window)
        self.ch_var_button = QPushButton(text="Wybierz sposób podparcia kół")
        self.ch_var_button.clicked.connect(self.popup.show)

        self.label_e2 = QLabelD("Przerwa między kołami")
        self.obl_srednice_labels = [QLabel(), QLabel(), QLabel()]
        self.accept_button = QPushButton(text="Zaktualizuj animację")

        self.errors = [
            QLabelD("Dla obecnych danych, otwory nie zmieszczą się w kole cykloidalnym."),
            QLabelD("Dla obecnych danych, otwory w kole cykloidalnym przecinają się."),
        ]

        for widget in self.input_widgets.values():
            if type(widget) == QComboBox:
                widget.currentIndexChanged.connect(self.inputs_modified)
            elif type(widget) == DoubleSpinBox or IntSpinBox:
                widget.valueChanged.connect(self.inputs_modified)
        self.accept_button.clicked.connect(self.button_clicked)
        
        self.setup_layout()
        self.inputs_modified()
        
        self.input_widgets["e2"].hide()
        self.label_e2.hide()
    
    def setup_layout(self):
        layout = QGridLayout()
        layout1 = QGridLayout()

        layout.addWidget(QLabelD("Ilość sworzni [n]"), 0, 0)
        layout.addWidget(self.input_widgets["n_sw"], 0, 1)
        layout.addWidget(QLabelD("Promień rozstawu sworzni [R<sub>wk</sub>]"), 1, 0)
        layout.addWidget(self.input_widgets["R_wk"], 1, 1)
        layout.addWidget(QLabelD("Materiał sworznia"), 2, 0)
        layout.addWidget(self.input_widgets["mat_sw"], 2, 1)
        layout.addWidget(QLabelD("Materiał tuleji"), 3, 0)
        layout.addWidget(self.input_widgets["mat_tul"], 3, 1)
        layout.addWidget(QLabelD("Grubość koła cykl. [b]"), 4, 0)
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
        layout1.addWidget(self.accept_button, 7, 0, 1, 3)
        for ind, widget in enumerate(self.errors):
            layout1.addWidget(widget, 8+ind, 0, 1, 3)
            widget.setStyleSheet("QLabel { color: red; }")
            widget.hide()

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout)
        layout_main.addLayout(layout1)
        self.setLayout(layout_main)

    def inputs_modified(self, kat=0):
        self.input_dane["n"] = self.input_widgets["n_sw"].value()
        self.input_dane["R_wk"] = self.input_widgets["R_wk"].value()
        self.input_dane["mat_sw"] = self.materialy[self.input_widgets["mat_sw"].currentText()]
        self.input_dane["mat_tul"] = self.materialy[self.input_widgets["mat_tul"].currentText()]
        self.input_dane["b"] = self.input_widgets["b"].value()
        self.input_dane["e1"] = self.input_widgets["e1"].value()
        self.input_dane["e2"] = self.input_widgets["e2"].value()
        self.input_dane["f_kt"] = self.input_widgets["f_kt"].value()
        self.input_dane["f_ts"] = self.input_widgets["f_ts"].value()
        self.input_dane["d_sw"] = self.input_widgets["d_sw"].value()
        self.input_dane["d_tul"] = self.input_widgets["d_tul"].value()
        self.input_dane["wsp_k"] = self.input_widgets["wsp_k"].value()
        
        wyniki = obliczenia_mech_wyjsciowy(self.input_dane, self.zew_dane, self.tol_data, self.obliczone_dane, kat)

        self.obliczone_dane["d_sw"] = wyniki["d_s_obl"]
        self.obl_srednice_labels[0].setText(str(wyniki["d_s_obl"]))
        self.input_widgets["d_sw"].modify(minimum=wyniki["d_s_obl"], maximum=wyniki["d_s_obl"]+10)
        self.input_dane["d_sw"] = self.input_widgets["d_sw"].value()
        self.obliczone_dane["d_tul"] = wyniki["d_t_obl"]
        self.obl_srednice_labels[1].setText(str(wyniki["d_t_obl"]))
        self.input_widgets["d_tul"].modify(minimum=self.obliczone_dane["d_tul"], maximum=self.obliczone_dane["d_tul"]+10)
        self.input_dane["d_tul"] = self.input_widgets["d_tul"].value()
        self.obliczone_dane["d_otw"] = wyniki["d_o_obl"]
        self.obl_srednice_labels[2].setText(str(wyniki["d_o_obl"]))

        self.wykresy_data_updated.emit({
            "sily": wyniki["sily"],
            "naciski": wyniki['naciski'],
            "straty": wyniki['straty'],
        })

    def button_clicked(self):
        for widget in self.errors:
            widget.hide()
        anim_data = {
            "n": self.input_dane["n"],
            "R_wk": self.input_dane["R_wk"],
            "d_sw": self.input_dane["d_sw"],
            "d_tul": self.input_dane["d_tul"],
            "d_otw": self.obliczone_dane["d_otw"],
        }
        if anim_data["R_wk"] + anim_data["d_otw"] / 2 >= self.zew_dane["R_f1"]:
            self.errors[0].show()
            self.anim_data_updated.emit({"wiktor": None})
        elif sprawdz_przecinanie_otworow(self.input_dane["R_wk"], self.input_dane["n"], self.obliczone_dane["d_otw"]):
            self.errors[1].show()
            self.anim_data_updated.emit({"wiktor": None})
        else:
            self.anim_data_updated.emit({"wiktor": anim_data})
    
    def close_choice_window(self, choice):
        self.input_dane["podparcie"] = choice
        self.popup.hide()
        self.inputs_modified()

    def tolerance_update(self, tol_data):
        self.tol_data = tol_data
        self.inputs_modified()


class ToleranceInput(QWidget):
    def __init__(self, parent, label_text):
        super().__init__(parent)
        self.tol = [0, 0, 0]

        self.label = QLabelD(label_text)
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
            "T_o": ToleranceInput(self, "T_o: Promienia otworu koła cykloidalnego"),
            "T_t": ToleranceInput(self, "T_t: Promienia zewnętrznego tulei"),
            "T_s": ToleranceInput(self, "T_t: Promienia zewnętrznego sworznia"),
            "T_Rk": ToleranceInput(self, "T_Rk: Promienia rozmieszczenia otworów w kole cykloidalnym"),
            "T_Rt": ToleranceInput(self, "T_Rt: Promienia rozmieszczenia tulei w elemencie wyjściowym"),
            "T_fi_k": ToleranceInput(self, "T_fi_k: Kątowego rozmieszczenia otworów w kole cykloidalnym"),
            "T_fi_t": ToleranceInput(self, "T_fi_t: Kątowego rozmieszczenia tulei w elemencie wyjściowym"),
            "T_e": ToleranceInput(self, "T_e: Mimośrodu"),
        }
        self.labels = { key: [QLabelD(key), QLabelD("0"), QLabelD("0"), QLabelD("0")] for key in self.fields }
        self.tolerancje = { key: widget.tol for key, widget in self.fields.items() }
        self.mode = "deviations"
        self.check = QCheckBox(text="Używaj luzów w obliczeniach")
        self.check.stateChanged.connect(self.on_check)

        self.label_top = QLabelD("Ustaw odchyłkę:")
        self.label_bottom = QLabelD("Obecne odchyłki:")

        self.tol_check = QCheckBox(text="Wybierz pole tolerancji")
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
            layout.addWidget(widget.label, 3+ind, 0)
            layout.addWidget(widget.low_input, 3+ind, 1)
            layout.addWidget(widget.high_input, 3+ind, 2)
            layout.addWidget(widget.deviation_input, 3+ind, 3)
            widget.setEnabled(False)
            widget.low_input.setEnabled(False)
            widget.high_input.setEnabled(False)
            widget.deviation_input.setEnabled(False)
        layout.addWidget(self.label_bottom, 11, 0, 1, 2)
        for ind, (l1, l2, l3, l4) in enumerate(self.labels.values()):
            layout.addWidget(l1, 12+ind, 0)
            layout.addWidget(l2, 12+ind, 1)
            layout.addWidget(l3, 12+ind, 2)
            layout.addWidget(l4, 12+ind, 3)
            l2.hide()
            l3.hide()
        layout.addWidget(self.accept_button)

        self.setLayout(layout)
        
    def on_check(self, state):
        enable = False if state == 0 else True
        self.accept_button.setEnabled(enable)
        self.tol_check.setEnabled(enable)
        self.dev_check.setEnabled(enable)
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


class Tab_Wiktor(AbstractTab):
    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        stacklayout = QStackedLayout()
        layout.addLayout(button_layout)
        layout.addLayout(stacklayout)
        self.data = DataEdit(self)
        self.wykresy = ChartTab()
        self.tol_edit = ToleranceEdit(self)
        self.data.wykresy_data_updated.connect(self.wykresy.update_charts)
        self.tol_edit.tolerance_data_updated.connect(self.data.tolerance_update)

        tab_titles = ["Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        stacked_widgets = [self.data, self.wykresy, self.tol_edit]

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button)
            stacklayout.addWidget(widget)
            button.pressed.connect(partial(stacklayout.setCurrentIndex, index))
        
        self.setLayout(layout)
    
    def send_data(self):
        ...
    
    def receive_data(self, new_data):
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
        self.data.inputs_modified()

    def save_data(self):
        self.data.inputs_modified()
        return {
            "input_dane": self.data.input_dane,
            "obliczone_dane": self.data.obliczone_dane,
            "zew_dane": self.data.zew_dane,
            "tolerancje": self.tol_edit.tolerancje
        }

    def load_data(self, new_data):
        if new_data is None:
            return
        self.data.input_dane = new_data.get("input_dane") if new_data.get("input_dane") else self.data.input_dane
        self.data.obliczone_dane = new_data.get("obliczone_dane") if new_data.get("obliczone_dane") else self.data.obliczone_dane
        self.data.zew_dane = new_data.get("zew_dane") if new_data.get("zew_dane") else self.data.zew_dane
        self.data.tolerancje = new_data.get("tolerancje") if new_data.get("tolerancje") else self.data.tolerancje
        self.data.inputs_modified()
