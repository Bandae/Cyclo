from PySide6.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QDoubleSpinBox, QPushButton, QHBoxLayout, QStackedLayout
from PySide6.QtCore import Signal
from pawlowe.wykresy import Wykresy
import math
from functools import partial
from abstract_tab import AbstractTab
from common_widgets import DoubleSpinBox, QLabelD

#TODO: pawel i wiktor tab, a takze nasze wykresy są tak podobne schematycznie, że może da rade z nich zrobić jakąś wspólną klase abstrakcyjną do dziedziczenia

class DataEdit(QWidget):
    wykresy_data_updated = Signal(int, dict)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout1 = QGridLayout()

                    #z    ro    h    g  a1 a2 f1 f2 w1 w2 b  rg g  e  h obc.   l_k   -> obc. - obciążenie wejsciowe! , l_k -> liczba kół
        self.dane = [24, 4.8, 0.625, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 500, 2]
        self.dane_materialowe = DaneMaterialowe()
        self.sily = None
        self.naprezenia = None
        self.refil_data()
        self.liczba_obciazonych_rolek = 0
        self.przyrost_kata = 360 / (self.dane[0] + 1)
        self.obliczenia_sil()

        self.spin_z = DoubleSpinBox(self.dane[0],8,38,1)
        self.spin_z.lineEdit().setReadOnly(True)
        self.spin_ro = DoubleSpinBox(self.dane[1],3,8,0.05)
        self.spin_h = DoubleSpinBox(self.dane[2],0.5,0.99,0.01)
        self.spin_g = DoubleSpinBox(self.dane[3],5,14,0.02)
        self.spin_obc = DoubleSpinBox(self.dane[15], 500, 5000, 10)
        self.spin_l_k = DoubleSpinBox(self.dane[16], 1, 4, 1)
        self.spin_l_k.lineEdit().setReadOnly(True)

        self.spin_z.valueChanged.connect(self.z_changed)
        self.spin_ro.valueChanged.connect(self.z_changed)
        self.spin_h.valueChanged.connect(self.z_changed)
        self.spin_g.valueChanged.connect(self.z_changed)
        self.spin_obc.valueChanged.connect(self.z_changed)
        self.spin_l_k.valueChanged.connect(self.z_changed)

        layout.addWidget(QLabelD("DANE WEJSCIOWE :"))
        layout.addWidget(QLabelD("Obciążenie wejsciowe [M]"))
        layout.addWidget(self.spin_obc)
        layout.addWidget(QLabelD("Liczba Kół [K]"))
        layout.addWidget(self.spin_l_k)
        layout.addWidget(QLabelD("Liczba Zębów [z]"))
        layout.addWidget(self.spin_z)
        layout.addWidget(QLabelD("Promień [ρ]"))
        layout.addWidget(self.spin_ro)
        layout.addWidget(QLabelD("Wsp. wysokości zęba [λ]"))
        layout.addWidget(self.spin_h)
        layout.addWidget(QLabelD("Promień rolek [g]"))
        layout.addWidget(self.spin_g)

        layout.addSpacing(10)

        data_label_text = ['Ra1:', 'Rf1:', 'Rw1:', 'Ra2:', 'Rf2:', 'Rw2:', 'Rb:', 'Rg:', 'g:', 'e:', 'h:']
        self.data_labels = {
            key: value for key, value in zip(
                data_label_text, [QLabelD(str(round(self.dane[ind], 2))) for ind in range(4, 15)]
            )
        }

        layout1.addWidget(QLabelD("DANE : "),0,0,1,2)
        for index, (text, qlabel) in enumerate(self.data_labels.items(), start=1):
            layout1.addWidget(QLabelD(text), index, 0)
            layout1.addWidget(qlabel, index, 1)
        layout_main = QHBoxLayout()
        layout_1 = QVBoxLayout()
        layout_1.addLayout(layout)
        layout_1.addLayout(layout1)
        layout_main.addLayout(layout_1)
        layout_main.addWidget(self.dane_materialowe)

        self.setLayout(layout_main)

    def refil_data(self):
        z=self.dane[0]
        ro=self.dane[1]
        lam=self.dane[2]
        g=self.dane[3]
        self.dane[4] = ro*(z+1+lam)-g
        self.dane[5] = ro*(z+1-lam)-g
        self.dane[6] = ro*lam*z
        self.dane[7] = ro*(z+1)-g
        self.dane[8] = ro*(z+1+(2*lam))-g
        self.dane[9] = ro*lam*(z+1)
        self.dane[10] = ro*z
        self.dane[11] = ro*(z+1)
        self.dane[12] = g
        self.dane[13] = ro*lam
        self.dane[14] = 2*self.dane[13]

    def refili_labels(self):
        # tutaj nie .items() tylko same wartosci zrobic
        for index, (text, qlabel) in enumerate(self.data_labels.items(), start=4):
            qlabel.setText(str(round(self.dane[index], 2)))

    def z_changed(self):
        self.dane[0] = self.spin_z.value()
        self.dane[1] = self.spin_ro.value()
        self.dane[2] = self.spin_h.value()
        self.dane[3] = self.spin_g.value()
        self.dane[15] = self.spin_obc.value()
        self.dane[16] = self.spin_l_k.value()

        h_min = (self.dane[0]-1)/(2*self.dane[0]+1)
        self.spin_h.setMinimum(h_min)

        self.refil_data()
        self.refili_labels()
        self.obliczenia_sil()

    def obliczenia_sil(self):
        if self.dane[0]%2==0:
            self.liczba_obciazonych_rolek = int(self.dane[0]/2)
        else :
            self.liczba_obciazonych_rolek = int((self.dane[0]+1)/2)-1
        self.przyrost_kata = 360/(self.dane[0]+1)
        
        sily = [None]*self.liczba_obciazonych_rolek
        alfa = [None] * self.liczba_obciazonych_rolek
        naprezenia = [None] * self.liczba_obciazonych_rolek
        Mk = self.dane[15]/self.dane[16]
        for a in range(self.liczba_obciazonych_rolek):
            i=a+1
            kat = i*self.przyrost_kata
            reke=((self.dane[1]*(self.dane[0]+1)*math.pow((1-(2*self.dane[2]*math.cos(self.dane[0]*kat*0.0175))+math.pow(self.dane[2],2)),(3/2)))/(1-(self.dane[2]*(self.dane[0]+2)*(math.cos(self.dane[0]*kat*0.0175)))+(math.pow(self.dane[2],2)*(self.dane[0]+1)))-(self.dane[3]))
            teta=i*self.przyrost_kata
            x=math.sqrt((math.pow(self.dane[10],2))+(math.pow(self.dane[6],2))-(2*self.dane[10]*self.dane[6]*math.cos(teta * 0.0175)))
            beta = math.degrees(math.asin(self.dane[10]*math.sin(teta * 0.0175)/x))
            alfa[a]=90-beta
            sily[a]=(4*Mk*math.cos(alfa[a] * 0.0175))/(self.dane[6]*(self.dane[0]+1))
            #naprezenia[a]=math.sqrt((sily[a]*(reke+self.dane[3]))/(self.dane_materialowe.dane_materialowe[4]*math.pi*reke*self.dane[3]*(((1-math.pow(self.dane_materialowe.dane_materialowe[2],2))/(self.dane_materialowe.dane_materialowe[0])))+((1-math.pow(self.dane_materialowe.dane_materialowe[3],2))/(self.dane_materialowe.dane_materialowe[1]))))
            naprezenia[a]=math.sqrt((sily[a]*(reke+self.dane[3]))/((self.dane_materialowe.dane_materialowe[4]*3.1415*reke*self.dane[3])*(((1-math.pow(self.dane_materialowe.dane_materialowe[2],2))/(self.dane_materialowe.dane_materialowe[0]))+((1-math.pow(self.dane_materialowe.dane_materialowe[3],2))/(self.dane_materialowe.dane_materialowe[1])))))
        self.sily=sily
        self.naprezenia=naprezenia

        self.wykresy_data_updated.emit(self.dane[0], {
            "sily": sily,
            "naprezenia": naprezenia,
        })


class Tab_Pawel(AbstractTab):
    anim_data_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        stacklayout = QStackedLayout()
        layout.addLayout(button_layout)
        layout.addLayout(stacklayout)
        self.data = DataEdit()
        self.wykresy = Wykresy()
        self.data.wykresy_data_updated.connect(self.wykresy.update_charts)

        tab_titles = ["Wprowadzanie Danych", "Wykresy"]
        stacked_widgets = [self.data, self.wykresy]
        buttons = []

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            buttons.append(QPushButton(title))
            button_layout.addWidget(buttons[index])
            stacklayout.addWidget(widget)
            buttons[index].pressed.connect(partial(stacklayout.setCurrentIndex, index))
        
        self.data.spin_z.valueChanged.connect(self.update_animation_data)
        self.data.spin_ro.valueChanged.connect(self.update_animation_data)
        self.data.spin_g.valueChanged.connect(self.update_animation_data)
        self.data.spin_h.valueChanged.connect(self.update_animation_data)
        
        self.setLayout(layout)

    def update_animation_data(self):
        self.anim_data_updated.emit({"pawel": self.data.dane})

    def send_data(self):
        return {"pawel": {
            "e": self.data.dane[13],
            "M": self.data.dane[15],
            "K": self.data.dane[16],
            "E_kola": self.data.dane_materialowe.dane_materialowe[0],
            "v_kola": self.data.dane_materialowe.dane_materialowe[2],
        }}
    
    def receive_data(self, new_data):
        ...


class DaneMaterialowe(QWidget):
    def __init__(self):
        super().__init__()
                            #     Y1         Y2     v1 v2   B
        self.dane_materialowe = [210000.0,210000.0,0.3,0.3,50]

        self.spin_Y1 = DoubleSpinBox(210000, 100000, 500000, 10000)
        self.spin_Y2 = DoubleSpinBox(self.dane_materialowe[1], 100000, 500000, 10000)
        self.spin_P1 = DoubleSpinBox(self.dane_materialowe[2], 0.1, 0.7, 0.02)
        self.spin_P2 = DoubleSpinBox(self.dane_materialowe[3], 0.1, 0.7, 0.02)
        self.spin_B = DoubleSpinBox(self.dane_materialowe[4], 20, 100, 2)

        layout = QVBoxLayout()
        layout.addWidget(QLabelD("DANE MATERIAŁOWE :"))
        layout.addWidget(QLabelD("Moduł Younga koła:"))
        layout.addWidget(self.spin_Y1)
        layout.addWidget(QLabelD("Moduł Younga rolki:"))
        layout.addWidget(self.spin_Y2)
        layout.addWidget(QLabelD("Liczba Poissona koła:"))
        layout.addWidget(self.spin_P1)
        layout.addWidget(QLabelD("Liczba Poissona rolki:"))
        layout.addWidget(self.spin_P2)
        layout.addWidget(QLabelD("Długość rolki:"))
        layout.addWidget(self.spin_B)
        layout.addSpacing(50)
        layout.addWidget(QLabelD("PRZYJĘTE LUZY :"))

        #Zmiana w danych :
        self.spin_Y1.valueChanged.connect(self.zmiana_danych)
        self.spin_Y2.valueChanged.connect(self.zmiana_danych)
        self.spin_P1.valueChanged.connect(self.zmiana_danych)
        self.spin_P2.valueChanged.connect(self.zmiana_danych)
        self.spin_B.valueChanged.connect(self.zmiana_danych)

        self.setLayout(layout)

    def zmiana_danych(self):
        self.dane_materialowe[0] = self.spin_Y1.value()
        self.dane_materialowe[1] = self.spin_Y2.value()
        self.dane_materialowe[2] = self.spin_P1.value()
        self.dane_materialowe[3] = self.spin_P2.value()
        self.dane_materialowe[4] = self.spin_B.value()
