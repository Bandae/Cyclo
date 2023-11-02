from PySide6.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QPushButton, QComboBox, QSpinBox, QHBoxLayout, QStackedLayout
from PySide6.QtCore import Signal
from Mech_wyj_tuleje.tuleje_obl import obliczenia_mech_wyjsciowy
from Mech_wyj_tuleje.wykresy import ChartTab
from functools import partial
from abstract_tab import AbstractTab
from common_widgets import DoubleSpinBox, QLabelD, IntSpinBox

# TODO: wyciagnac od Pawla jeszcze srednice wewnetrzna kola
# TODO: sily wychodza ujemnie
# TODO: v i E kola juz przyjete od Pawla, uzyc ich

class DataEdit(QWidget):
    wykresy_data_updated = Signal(dict)
    anim_data_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        self.input_dane = {
            "M_k": 500,
            "n": 8,
            "R_wk": 80,
            "mat_sw": "17Cr3",
            "mat_tul": "17Cr3",
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
        self.data.wykresy_data_updated.connect(self.wykresy.update_charts)

        tab_titles = ["Wprowadzanie Danych", "Wykresy"]
        stacked_widgets = [self.data, self.wykresy]
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
        if dane_pawla is not None:
            for key in dane_pawla:
                self.data.zew_dane[key] = dane_pawla[key]
