from PySide6.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QDoubleSpinBox, QPushButton, QComboBox, QSpinBox
from Mech_wyj_tuleje.tuleje_obl import obliczenia_mech_wyjsciowy

# TODO: wyciagnac mimosrod od Pawla jakos i inne dane

class DataEdit(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        layout = QGridLayout()
        layout1 = QGridLayout()
        
        self.input_dane = {
            "M_k": 500,
            "n": 8,
            "R_wk": 80,
            "k_g": 300,
            "E": 210000,
            "b": 25,
            "podparcie": "jedno koło cykloidalne",
            "d_sw": 0,
            "d_tul": 0,
            "wsp_k": 0,
            "e1": 1,
            "e2": 1,
        }
        self.obliczone_dane = {
            "d_sw": 20,
            "d_tul": 20,
            "d_otw": 20
        }
        self.mimosrod = 3

        # TODO: zmienic dokladnie te min i maxy

        # self.input_widgets = {

        # }

        self.spin_obc = DoubleSpinBox(self.input_dane["M_k"], 200, 5000, 10)
        self.spin_n_sw = IntSpinBox(self.input_dane["n"], 4, 16, 1)
        self.spin_R_wk = DoubleSpinBox(self.input_dane["R_wk"], 80, 200, 1)
        self.spin_k_g = DoubleSpinBox(self.input_dane["k_g"], 100, 400, 1)
        self.spin_E = DoubleSpinBox(self.input_dane["E"], 10000, 300000, 1)
        self.spin_b = DoubleSpinBox(self.input_dane["b"], 5, 30, 0.1)

        self.dropd_wariant = QComboBox()
        self.dropd_wariant.addItems([
            "jedno koło cykloidalne",
            "jedno koło, jeden koniec zamocowany, luźne śruby",
            "jedno koło, jeden koniec zamocowany, ciasne śruby",
            "dwa koła",
            "dwa koła, jeden koniec zamocowany, luźne śruby",
            "dwa koła jeden koniec zamocowany, ciasne śruby"
        ])

        self.spin_e1 = DoubleSpinBox(self.input_dane["e1"], 0, 5, 0.05)
        self.label_e2 = QLabelD("Przerwa między kołami")
        self.spin_e2 = DoubleSpinBox(self.input_dane["e2"], 0, 5, 0.05)

        self.spin_obc.valueChanged.connect(self.oblicz_srednice_sworzni)
        self.spin_n_sw.valueChanged.connect(self.oblicz_srednice_sworzni)
        self.spin_R_wk.valueChanged.connect(self.oblicz_srednice_sworzni)
        self.spin_k_g.valueChanged.connect(self.oblicz_srednice_sworzni)
        self.spin_E.valueChanged.connect(self.oblicz_srednice_sworzni)
        self.spin_b.valueChanged.connect(self.oblicz_srednice_sworzni)
        self.dropd_wariant.currentIndexChanged.connect(self.oblicz_srednice_sworzni)
        self.spin_e1.valueChanged.connect(self.oblicz_srednice_sworzni)
        self.spin_e2.valueChanged.connect(self.oblicz_srednice_sworzni)

        layout.addWidget(QLabelD("DANE WEJSCIOWE :"), 0, 0, 1, 2)
        layout.addWidget(QLabelD("Obciążenie [Mk]"), 1, 0)
        layout.addWidget(self.spin_obc, 1, 1)
        layout.addWidget(QLabelD("Ilość sworzni [n]"), 2, 0)
        layout.addWidget(self.spin_n_sw, 2, 1)
        layout.addWidget(QLabelD("Promień rozstawu sworzni [R_wk]"), 3, 0)
        layout.addWidget(self.spin_R_wk, 3, 1)
        layout.addWidget(QLabelD("k_g mat. sworznia [k_g]"), 4, 0)
        layout.addWidget(self.spin_k_g, 4, 1)
        layout.addWidget(QLabelD("E mat. sworznia [E]"), 5, 0)
        layout.addWidget(self.spin_E, 5, 1)
        layout.addWidget(QLabelD("Grubość koła cykl. [b]"), 6, 0)
        layout.addWidget(self.spin_b, 6, 1)

        layout.addWidget(QLabelD("Wariant podparcia"), 7, 0)
        layout.addWidget(self.dropd_wariant, 7, 1)

        layout.addWidget(QLabelD("Przerwa między kołem a tarczą"), 8, 0)
        layout.addWidget(self.spin_e1, 8, 1)
        layout.addWidget(self.label_e2, 9, 0)
        layout.addWidget(self.spin_e2, 9, 1)

        layout1.addWidget(QLabelD("Obliczone średnice:"), 0, 0, 1, 3)
        layout1.addWidget(QLabelD("sworznia"), 1, 0)
        layout1.addWidget(QLabelD("tuleji"), 1, 1)
        layout1.addWidget(QLabelD("otworów"), 1, 2)

        self.obl_srednice_labels = [QLabel(), QLabel(), QLabel()]
        self.spin_wsp_k = DoubleSpinBox(1.3, 1.2, 1.5, 0.05)
        self.spin_wsp_k.valueChanged.connect(self.oblicz_srednice_tuleji)
        self.spin_sr_sw = DoubleSpinBox(6,5,14,0.2)
        self.spin_sr_sw.valueChanged.connect(self.oblicz_srednice_tuleji)
        self.spin_sr_tul = DoubleSpinBox(6,5,14,0.2)
        self.spin_sr_tul.valueChanged.connect(self.oblicz_srednice_otworow)
        self.accept_button = QPushButton(text="Zaktualizuj animację")
        self.accept_button.clicked.connect(self.button_clicked)

        layout1.addWidget(self.obl_srednice_labels[0], 2, 0)
        layout1.addWidget(self.obl_srednice_labels[1], 2, 1)
        layout1.addWidget(self.obl_srednice_labels[2], 2, 2)
        layout1.addWidget(QLabelD("Współczynnik grubości ścianki tuleji"), 3, 0)
        layout1.addWidget(self.spin_wsp_k, 3, 1)
        layout1.addWidget(QLabelD("Dobierz średnice:"), 4, 0, 1, 3)
        layout1.addWidget(QLabelD("sworznia"), 5, 0)
        layout1.addWidget(QLabelD("tuleji"), 5, 1)
        layout1.addWidget(self.spin_sr_sw, 6, 0)
        layout1.addWidget(self.spin_sr_tul, 6, 1)
        layout1.addWidget(self.accept_button, 7, 0, 1, 3)

        self.spin_sr_sw.hide()
        self.spin_sr_tul.hide()
        self.spin_wsp_k.hide()
        self.label_e2.hide()
        self.spin_e2.hide()

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout)
        layout_main.addLayout(layout1)
        self.setLayout(layout_main)

    def oblicz_srednice_sworzni(self):
        self.input_dane["M_k"] = self.spin_obc.value()
        self.input_dane["n"] = self.spin_n_sw.value()
        self.input_dane["R_wk"] = self.spin_R_wk.value()
        self.input_dane["k_g"] = self.spin_k_g.value()
        self.input_dane["E"] = self.spin_E.value()
        self.input_dane["b"] = self.spin_b.value()
        self.input_dane["podparcie"] = self.dropd_wariant.currentText()
        
        wyniki = obliczenia_mech_wyjsciowy(
            self.input_dane["podparcie"], self.input_dane["k_g"], 
            self.input_dane["E"], self.input_dane["b"], self.input_dane["n"], 
            self.input_dane["M_k"], self.input_dane["R_wk"]
        )
        d_sw = round(wyniki["d_smax"], 2)
        self.obliczone_dane["d_sw"] = d_sw
        self.obl_srednice_labels[0].setText(str(d_sw))

        self.spin_sr_sw.modify(minimum=d_sw)
        min_sr_tul = d_sw * self.input_dane["wsp_k"]
        self.spin_sr_tul.modify(minimum=min_sr_tul)

        if self.dropd_wariant.currentIndex() >= 3:
            self.label_e2.show()
            self.spin_e2.show()
        else:
            self.label_e2.hide()
            self.spin_e2.hide()

        self.spin_sr_sw.show()
        self.spin_wsp_k.show()

    def oblicz_srednice_tuleji(self):
        self.input_dane["d_sw"] = self.spin_sr_sw.value()
        self.input_dane["wsp_k"] = self.spin_wsp_k.value()

        self.obliczone_dane["d_tul"] = round(self.input_dane["d_sw"] * self.input_dane["wsp_k"], 2)
        self.obl_srednice_labels[1].setText(str(self.obliczone_dane["d_tul"]))

        self.spin_sr_tul.modify(minimum=self.obliczone_dane["d_tul"])

        self.spin_sr_tul.show()

    def oblicz_srednice_otworow(self):
        self.input_dane["d_tul"] = self.spin_sr_tul.value()

        self.obliczone_dane["d_otw"] = round(self.input_dane["d_tul"] + (2 * self.mimosrod), 2)
        self.obl_srednice_labels[2].setText(str(self.obliczone_dane["d_otw"]))

    def button_clicked(self):
        self.anim_data = {
            "n": self.input_dane["n"],
            "R_wk": self.input_dane["R_wk"],
            "d_sw": self.input_dane["d_sw"],
            "d_tul": self.input_dane["d_tul"],
            "d_otw": self.obliczone_dane["d_otw"],
        }
        if all(self.anim_data.values()):
            self.parent.parent.update_animation_data()
        
    def obliczenia_sil(self):
        Mk = self.dane[15] / self.dane[16]


class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self,a,b,c,d):
        super().__init__()
        self.setValue(a)
        self.lineEdit().setReadOnly(False)
        self.setRange(b, c)
        self.setSingleStep(d)
    
    def modify(self, value=None, minimum=None, maximum=None):
        if minimum is not None:
            self.setMinimum(minimum)
        if maximum is not None:
            self.setMaximum(maximum)
        if value is not None:
            self.setValue(value)


class IntSpinBox(QSpinBox):
    def __init__(self,a,b,c,d):
        super().__init__()

        self.setValue(a)
        self.lineEdit().setReadOnly(False)
        self.setRange(b, c)
        self.setSingleStep(d)


class Tab_Wiktor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.layout = QGridLayout()
        self.data = DataEdit(self)

        self.layout.addWidget(self.data,0,0,4,1)
        self.setLayout(self.layout)


class QLabelD(QLabel):
    def __init__(self,a):
        super().__init__()

        self.setText(str(a))
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
