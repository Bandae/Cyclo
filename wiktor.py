from PySide6.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QDoubleSpinBox, QPushButton, QComboBox
from Mech_wyj_tuleje.tuleje_obl import obliczenia_mech_wyjsciowy

class DataEdit(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout1 = QGridLayout()
        
        self.input_dane = {
            "M_k": 500,
            "n": 8,
            "R_wt": 80,
            "k_g": 300,
            "E": 210000,
            "b": 25,
            "podparcie": "jedno koło cykloidalne",
            "d_sw": None,
            "d_tul": None,
        }
        
        self.obliczone_dane = {
            "d_sw": 20,
            "d_tul": 20,
            "d_otw": 20
        }

        self.refil_data()

        # TODO: zmienic dokladnie te min i maxy
        self.spin_obc = SpinBox(self.input_dane["M_k"], 500, 5000, 10)
        self.spin_n_sw = SpinBox(self.input_dane["n"], 1, 4, 1)
        self.spin_n_sw.lineEdit().setReadOnly(True)
        self.spin_R_wt = SpinBox(self.input_dane["R_wt"],8,38,1)
        self.spin_R_wt.lineEdit().setReadOnly(True)
        self.spin_k_g = SpinBox(self.input_dane["k_g"],3,8,0.05)
        self.spin_E = SpinBox(self.input_dane["E"],0.5,0.99,0.01)
        self.spin_b = SpinBox(self.input_dane["b"],5,14,0.02)

        self.dropd_wariant = QComboBox()
        self.dropd_wariant.addItems([
            "jedno koło cykloidalne",
            "jedno koło, jeden koniec zamocowany, luźne śruby",
            "jedno koło, jeden koniec zamocowany, ciasne śruby",
            "dwa koła",
            "dwa koła, jeden koniec zamocowany, luźne śruby",
            "dwa koła jeden koniec zamocowany, ciasne śruby"
        ])

        self.spin_obc.valueChanged.connect(self.input_changed)
        self.spin_n_sw.valueChanged.connect(self.input_changed)
        self.spin_R_wt.valueChanged.connect(self.input_changed)
        self.spin_k_g.valueChanged.connect(self.input_changed)
        self.spin_E.valueChanged.connect(self.input_changed)
        self.spin_b.valueChanged.connect(self.input_changed)
        self.dropd_wariant.currentIndexChanged.connect(self.input_changed)

        layout.addWidget(QLabelD("DANE WEJSCIOWE :"))
        layout.addWidget(QLabelD("Obciążenie [Mk]"))
        layout.addWidget(self.spin_obc)
        layout.addWidget(QLabelD("Ilość sworzni [n]"))
        layout.addWidget(self.spin_n_sw)
        layout.addWidget(QLabelD("Promień rozstawu sworzni [R_wt]"))
        layout.addWidget(self.spin_R_wt)
        layout.addWidget(QLabelD("k_g mat. sworznia [k_g]"))
        layout.addWidget(self.spin_k_g)
        layout.addWidget(QLabelD("E mat. sworznia [E]"))
        layout.addWidget(self.spin_E)
        layout.addWidget(QLabelD("Grubość koła cykl. [b]"))
        layout.addWidget(self.spin_b)

        layout.addWidget(QLabelD("Wariant podparcia"))
        layout.addWidget(self.dropd_wariant)

        layout.addSpacing(10)

        layout1.addWidget(QLabelD("Obliczone średnice:"), 0, 0, 1, 3)
        layout1.addWidget(QLabelD("sworznia"), 1, 0)
        layout1.addWidget(QLabelD("tuleji"), 1, 1)
        layout1.addWidget(QLabelD("otworów"), 1, 2)
        layout1.addWidget(QLabelD("otworów"), 2, 0)
        layout1.addWidget(QLabelD("otworów"), 2, 1)
        layout1.addWidget(QLabelD("otworów"), 2, 2)
        layout1.addWidget(QLabelD("Współczynnik grubości ścianki tuleji"), 3, 0)
        self.spin_sr_sw = SpinBox(6,5,14,0.2)
        layout1.addWidget(self.spin_sr_sw, 3, 1)
        layout1.addWidget(QLabelD("Dobierz średnice:"), 4, 0, 1, 3)
        layout1.addWidget(QLabelD("sworznia"), 5, 0)
        layout1.addWidget(QLabelD("tuleji"), 5, 1)
        self.spin_sr_sw = SpinBox(6,5,14,0.2)
        self.spin_sr_tul = SpinBox(6,5,14,0.2)
        layout1.addWidget(self.spin_sr_sw, 6, 0)
        layout1.addWidget(self.spin_sr_tul, 6, 1)
        self.accept_button = QPushButton(text="Zaktualizuj animację")
        self.accept_button.clicked.connect(self.button_clicked)
        layout1.addWidget(self.accept_button, 7, 0, 1, 3)

            
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout)
        layout_main.addLayout(layout1)
        self.setLayout(layout_main)

    def refil_data(self):
        wyniki = obliczenia_mech_wyjsciowy(self.input_dane["podparcie"], self.input_dane["k_g"], self.input_dane["E"], self.input_dane["b"], self.input_dane["n"], self.input_dane["M_k"], self.input_dane["R_wt"])
        self.obliczone_dane["d_sw"] = wyniki["d_smax"]

    def refili_labels(self):
        ...

    def input_changed(self):
        ...
        # self.input_dane[0] = self.spin_R_wt.value()
        # self.input_dane[1] = self.spin_k_g.value()
        # self.input_dane[2] = self.spin_E.value()
        # self.input_dane[3] = self.spin_b.value()
        # self.input_dane[15] = self.spin_obc.value()
        # self.input_dane[16] = self.spin_n_sw.value()

        # h_min = (self.input_dane[0]-1)/(2*self.input_dane[0]+1)
        # self.spin_E.setMinimum(h_min)

    def button_clicked(self):
        ...
        

    def obliczenia_sil(self):
        Mk = self.dane[15]/self.dane[16]


class SpinBox(QDoubleSpinBox):
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
        self.data = DataEdit()

        self.data.spin_R_wt.valueChanged.connect(self.update_animation_data)
        self.data.spin_k_g.valueChanged.connect(self.update_animation_data)
        self.data.spin_b.valueChanged.connect(self.update_animation_data)
        self.data.spin_E.valueChanged.connect(self.update_animation_data)

        self.layout.addWidget(self.data,0,0,4,1)
        self.setLayout(self.layout)
    
    def update_animation_data(self):
        self.parent.update_animation_data()


class QLabelD(QLabel):
    def __init__(self,a):
        super().__init__()

        self.setText(str(a))
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
