from PySide6.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QDoubleSpinBox, QPushButton
from PySide6.QtCore import Signal
from pawlowe.wykresy import Wykresy
import math
from widgets import AbstractTab

class DataEdit(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout1 = QGridLayout()

                    #z    ro    h    g  a1 a2 f1 f2 w1 w2 b  rg g  e  h obc.   l_k   -> obc. - obciążenie wejsciowe! , l_k -> liczba kół
        self.dane = [24, 4.8, 0.625, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 500, 2]
        self.sily = None
        self.refil_data()
        self.liczba_obciazonych_rolek = 0
        self.przyrost_kata = 360 / (self.dane[0] + 1)
        self.obliczenia_sil()
        self.spin_z = SpinBox(self.dane[0],8,38,1)
        self.spin_z.lineEdit().setReadOnly(True)
        self.spin_ro = SpinBox(self.dane[1],3,8,0.05)
        self.spin_h = SpinBox(self.dane[2],0.5,0.99,0.01)
        self.spin_g = SpinBox(self.dane[3],5,14,0.02)
        self.spin_obc = SpinBox(self.dane[15], 500, 5000, 10)
        self.spin_l_k = SpinBox(self.dane[16], 1, 4, 1)
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

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout)
        layout_main.addLayout(layout1)
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
        #print(str(h_min))
        self.spin_h.setMinimum(h_min)

        self.refil_data()
        self.refili_labels()
        self.obliczenia_sil()
        print(self.sily)

    def obliczenia_sil(self):
        if self.dane[0]%2==0:
            self.liczba_obciazonych_rolek = int(self.dane[0]/2)
        else :
            self.liczba_obciazonych_rolek = int((self.dane[0]+1)/2)-1
        self.przyrost_kata = 360/(self.dane[0]+1)
        print(str(self.liczba_obciazonych_rolek))
        sily = [None]*self.liczba_obciazonych_rolek
        alfa = [None] * self.liczba_obciazonych_rolek
        Mk = self.dane[15]/self.dane[16]
        for a in range(self.liczba_obciazonych_rolek):
            i=a+1
            teta=i*self.przyrost_kata
            x=math.sqrt((math.pow(self.dane[10],2))+(math.pow(self.dane[6],2))-(2*self.dane[10]*self.dane[6]*math.cos(teta * 0.0175)))
            beta = math.degrees(math.asin(self.dane[10]*math.sin(teta * 0.0175)/x))
            alfa[a]=90-beta
            sily[a]=(4*Mk*math.cos(alfa[a] * 0.0175))/(self.dane[6]*(self.dane[0]+1))
        print(alfa)
        self.sily=sily

class SpinBox(QDoubleSpinBox):
    def __init__(self,a,b,c,d):
        super().__init__()

        self.setValue(a)
        self.lineEdit().setReadOnly(False)
        self.setRange(b, c)
        self.setSingleStep(d)

class Tab_Pawel(AbstractTab):
    anim_data_updated = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.layout = QGridLayout()
        self.data = DataEdit()
        self.data.spin_z.valueChanged.connect(self.update_animation_data)
        self.data.spin_ro.valueChanged.connect(self.update_animation_data)
        self.data.spin_g.valueChanged.connect(self.update_animation_data)
        self.data.spin_h.valueChanged.connect(self.update_animation_data)

        self.layout.addWidget(self.data,0,0,4,1)
        self.setLayout(self.layout)

    def update_animation_data(self):
        self.anim_data_updated.emit({"pawel": self.data.dane})


class QLabelD(QLabel):
    def __init__(self,a):
        super().__init__()

        self.setText(str(a))
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)
