from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QStackedLayout, QCheckBox
from PySide6.QtCore import Signal, Qt
from Mech_wyj_tuleje.tuleje_obl import obliczenia_mech_wyjsciowy
from Mech_wyj_tuleje.wykresy import ChartTab
from functools import partial
from abstract_tab import AbstractTab
from common_widgets import DoubleSpinBox, QLabelD, IntSpinBox

# TODO: wyciagnac od Pawla jeszcze srednice wewnetrzna kola
# TODO: sily wychodza ujemnie

class DataEdit(QWidget):
    wykresy_data_updated = Signal(dict)
    anim_data_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        self.input_dane = {
            "M_k": 500,
            "n": 8,
            "R_wk": 80,
            "mat_sw": {"E": 210000, "v": 0.3, "k_g": 300},
            "mat_tul": {"E": 210000, "v": 0.3, "k_g": 300},
            "b": 25,
            "podparcie": "jedno koło cykloidalne",
            "d_sw": 0,
            "d_tul": 1,
            "wsp_k": 0,
            "e1": 1,
            "e2": 1,
        }
        self.obliczone_dane = {
            "d_sw": 20,
            "d_tul": 20,
            "d_otw": 20
        }
        self.zew_dane = {
            "e": 3,
            "M": 500,
            "K": 1,
            "E_kola": 210000,
            "v_kola": 0.3,
        }
        # TODO: ostatecznie brac z bazy danych
        self.materialy = {
            "17Cr3": {"E": 210000, "v": 0.3, "k_g": 300},
            "20MnCr5": {"E": 210000, "v": 0.3, "k_g": 450},
            "C45": {"E": 210000, "v": 0.3, "k_g": 205},
        }

        # TODO: zmienic dokladnie te min i maxy
        self.input_widgets = {
            "n_sw": IntSpinBox(self.input_dane["n"], 4, 16, 1),
            "R_wk": DoubleSpinBox(self.input_dane["R_wk"], 80, 200, 1),
            "mat_sw": QComboBox(),
            "mat_tul": QComboBox(),
            "b": DoubleSpinBox(self.input_dane["b"], 5, 30, 0.1),
            "wariant": QComboBox(),
            "e1": DoubleSpinBox(self.input_dane["e1"], 0, 5, 0.05),
            "e2": DoubleSpinBox(self.input_dane["e2"], 0, 5, 0.05),
            "wsp_k": DoubleSpinBox(1.3, 1.2, 1.5, 0.05),
            "d_sw": DoubleSpinBox(6, 5, 14, 0.1),
            "d_tul": DoubleSpinBox(6, 5, 14, 0.1),
        }

        self.input_widgets["mat_sw"].addItems([mat for mat in self.materialy])
        self.input_widgets["mat_tul"].addItems([mat for mat in self.materialy])
        self.input_widgets["wariant"].addItems([
            "jedno koło cykloidalne",
            "jedno koło, jeden koniec zamocowany, luźne śruby",
            "jedno koło, jeden koniec zamocowany, ciasne śruby",
            "dwa koła",
            "dwa koła, jeden koniec zamocowany, luźne śruby",
            "dwa koła jeden koniec zamocowany, ciasne śruby"
        ])

        self.label_e2 = QLabelD("Przerwa między kołami")
        self.obl_srednice_labels = [QLabel(), QLabel(), QLabel()]
        self.accept_button = QPushButton(text="Zaktualizuj animację")

        for widget in self.input_widgets.values():
            if type(widget) == QComboBox:
                widget.currentIndexChanged.connect(self.inputs_modified)
            else:
                widget.valueChanged.connect(self.inputs_modified)
        self.accept_button.clicked.connect(self.button_clicked)
        
        self.setup_layout()
        self.input_widgets["d_sw"].hide()
        self.input_widgets["d_tul"].hide()
        self.input_widgets["wsp_k"].hide()
        self.input_widgets["e2"].hide()
        self.label_e2.hide()
    
    def setup_layout(self):
        layout = QGridLayout()
        layout1 = QGridLayout()

        layout.addWidget(QLabelD("DANE WEJSCIOWE :"), 0, 0, 1, 2)
        layout.addWidget(QLabelD("Ilość sworzni [n]"), 2, 0)
        layout.addWidget(self.input_widgets["n_sw"], 2, 1)
        layout.addWidget(QLabelD("Promień rozstawu sworzni [R_wk]"), 3, 0)
        layout.addWidget(self.input_widgets["R_wk"], 3, 1)
        layout.addWidget(QLabelD("Materiał sworznia"), 4, 0)
        layout.addWidget(self.input_widgets["mat_sw"], 4, 1)
        layout.addWidget(QLabelD("Materiał tuleji"), 5, 0)
        layout.addWidget(self.input_widgets["mat_tul"], 5, 1)
        layout.addWidget(QLabelD("Grubość koła cykl. [b]"), 6, 0)
        layout.addWidget(self.input_widgets["b"], 6, 1)

        layout.addWidget(QLabelD("Wariant podparcia"), 7, 0)
        layout.addWidget(self.input_widgets["wariant"], 7, 1)

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
        layout1.addWidget(QLabelD("Współczynnik grubości ścianki tuleji"), 3, 0)
        layout1.addWidget(self.input_widgets["wsp_k"], 3, 1)
        layout1.addWidget(QLabelD("Dobierz średnice:"), 4, 0, 1, 3)
        layout1.addWidget(QLabelD("sworznia"), 5, 0)
        layout1.addWidget(QLabelD("tuleji"), 5, 1)
        layout1.addWidget(self.input_widgets["d_sw"], 6, 0)
        layout1.addWidget(self.input_widgets["d_tul"], 6, 1)
        layout1.addWidget(self.accept_button, 7, 0, 1, 3)

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout)
        layout_main.addLayout(layout1)
        self.setLayout(layout_main)

    def inputs_modified(self):
        self.input_dane["n"] = self.input_widgets["n_sw"].value()
        self.input_dane["R_wk"] = self.input_widgets["R_wk"].value()
        self.input_dane["mat_sw"] = self.materialy[self.input_widgets["mat_sw"].currentText()]
        self.input_dane["mat_tul"] = self.materialy[self.input_widgets["mat_tul"].currentText()]
        self.input_dane["b"] = self.input_widgets["b"].value()
        self.input_dane["podparcie"] = self.input_widgets["wariant"].currentText()
        self.input_dane["e1"] = self.input_widgets["e1"].value()
        self.input_dane["e2"] = self.input_widgets["e2"].value()
        
        wyniki = obliczenia_mech_wyjsciowy(self.input_dane, self.zew_dane, self.obliczone_dane["d_otw"])
        d_sw = round(wyniki["d_smax"], 2)
        self.obliczone_dane["d_sw"] = d_sw
        self.obl_srednice_labels[0].setText(str(d_sw))

        self.wykresy_data_updated.emit({
            "sily": wyniki["sily"],
        })

        self.input_widgets["d_sw"].modify(minimum=d_sw, maximum=d_sw+10)
        self.input_dane["d_sw"] = self.input_widgets["d_sw"].value()
        self.input_dane["wsp_k"] = self.input_widgets["wsp_k"].value()

        self.obliczone_dane["d_tul"] = round(self.input_dane["d_sw"] * self.input_dane["wsp_k"], 2)
        self.obl_srednice_labels[1].setText(str(self.obliczone_dane["d_tul"]))
        self.input_widgets["d_tul"].modify(minimum=self.obliczone_dane["d_tul"], maximum=self.obliczone_dane["d_tul"]+10)
        self.input_dane["d_tul"] = self.input_widgets["d_tul"].value()

        self.obliczone_dane["d_otw"] = round(self.input_dane["d_tul"] + (2 * self.zew_dane["e"]), 2)
        self.obl_srednice_labels[2].setText(str(self.obliczone_dane["d_otw"]))

        self.wykresy_data_updated.emit({
            "naciski": obliczenia_mech_wyjsciowy(self.input_dane, self.zew_dane, self.obliczone_dane["d_otw"])['naciski'],
        })

        if self.input_widgets["wariant"].currentIndex() >= 3:
            self.label_e2.show()
            self.input_widgets["e2"].show()
        else:
            self.label_e2.hide()
            self.input_widgets["e2"].hide()

        self.input_widgets["d_sw"].show()
        self.input_widgets["wsp_k"].show()
        self.input_widgets["d_tul"].show()

    def button_clicked(self):
        anim_data = {
            "n": self.input_dane["n"],
            "R_wk": self.input_dane["R_wk"],
            "d_sw": self.input_dane["d_sw"],
            "d_tul": self.input_dane["d_tul"],
            "d_otw": self.obliczone_dane["d_otw"],
        }
        if all(anim_data.values()):
            self.anim_data_updated.emit({"wiktor": anim_data})


class ToleranceInput(QWidget):
    def __init__(self, parent, label_text):
        super().__init__(parent)
        self.tol = [0, 0]

        label = QLabelD(label_text)
        self.low_input = DoubleSpinBox(self.tol[0], -0.05, 0.05, 0.001)
        self.high_input = DoubleSpinBox(self.tol[1], -0.05, 0.05, 0.001)

        self.low_input.setDecimals(3)
        self.high_input.setDecimals(3)

        self.low_input.valueChanged.connect(self.modified_low)
        self.high_input.valueChanged.connect(self.modified_high)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.low_input, 0, 1)
        layout.addWidget(self.high_input, 0, 2)
        self.setLayout(layout)
    
    def modified_low(self):
        self.tol[0] = round(self.low_input.value(), 3)
        self.high_input.modify(minimum=self.tol[0])
        # self.low_input.modify(maximum=self.tol[1])
    
    def modified_high(self):
        self.tol[1] = round(self.high_input.value(), 3)
        self.low_input.modify(maximum=self.tol[1])
        # self.high_input.modify(minimum=self.tol[0])


class ToleranceEdit(QWidget):
    tolerance_data_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        # przepraszam za to
        self.fields = {
            "T_o": ToleranceInput(self, "T_o: Promienia otworu koła cykloidalnego" + 37 * " "),
            "T_t": ToleranceInput(self, "T_t: Promienia zewnętrznego tulei" + 51 * " "),
            "T_Rk": ToleranceInput(self, "T_Rk: Promienia rozmieszczenia otworów w kole cykloidalnym" + " "),
            "T_Rt": ToleranceInput(self, "T_Rt: Promienia rozmieszczenia tulei w elemencie wyjściowym" + " "),
            "T_fi_k": ToleranceInput(self, "T_fi_k: Kątowego rozmieszczenia otworów w kole cykloidalnym"),
            "T_fi_t": ToleranceInput(self, "T_fi_t: Kątowego rozmieszczenia tulei w elemencie wyjściowym"),
            "T_e": ToleranceInput(self, "T_e: Mimośrodu" + 82 * " "),
        }
        self.labels = { key: [QLabelD(key), QLabelD("0"), QLabelD("0")] for key in self.fields }
        self.tolerancje = { key: widget.tol for key, widget in self.fields.items() }
        self.check = QCheckBox(text="Używaj luzów w obliczeniach")
        self.check.stateChanged.connect(self.on_check)
        self.accept_button = QPushButton(text="Ustaw tolerancje")
        self.accept_button.clicked.connect(self.data_updated)
        self.accept_button.setEnabled(False)

        layout = QGridLayout()
        layout.addWidget(self.check, 0, 0)
        layout.addWidget(QLabelD("Tolerancja:"), 1, 0, 1, 3)
        for ind, widget in enumerate(self.fields.values()):
            # widget.low_input.valueChanged.connect(self.data_updated)
            # widget.high_input.valueChanged.connect(self.data_updated)
            layout.addWidget(widget, 2+ind, 0)
            widget.setEnabled(False)
        layout.addWidget(QLabelD("Obecne tolerancje:"), 9, 0, 1, 2)
        for ind, (l1, l2, l3) in enumerate(self.labels.values()):
            layout.addWidget(l1, 10+ind, 0)
            layout.addWidget(l2, 10+ind, 1)
            layout.addWidget(l3, 10+ind, 2)
        layout.addWidget(self.accept_button)

        self.setLayout(layout)
    
    def on_check(self, state):
        enable = False if state == 0 else True
        self.accept_button.setEnabled(enable)
        for widget in self.fields.values():
            widget.setEnabled(enable)
            self.accept_button.setEnabled(enable)
        if enable:
            self.data_updated()
        else:
            for (_, l2, l3) in self.labels.values():
                l2.setText("0")
                l3.setText("0")

    def data_updated(self):
        for key, widget in self.fields.items():
            for ind in range(2):
                temp_text = str(widget.tol[ind]) if widget.tol[ind] <= 0 else "+" + str(widget.tol[ind])
                self.labels[key][ind+1].setText(temp_text)
        self.tolerance_data_updated.emit(self.tolerancje)


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

        tab_titles = ["Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        stacked_widgets = [self.data, self.wykresy, self.tol_edit]
        buttons = []

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            buttons.append(QPushButton(title))
            button_layout.addWidget(buttons[index])
            stacklayout.addWidget(widget)
            buttons[index].pressed.connect(partial(stacklayout.setCurrentIndex, index))
        
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
