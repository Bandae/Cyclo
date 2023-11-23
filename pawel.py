from PySide2.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QDoubleSpinBox, QPushButton, QHBoxLayout, QStackedLayout
from PySide2.QtCore import Signal
from pawlowe.wykresy import Wykresy
import math
from functools import partial
from abstract_tab import AbstractTab
from common_widgets import DoubleSpinBox, QLabelD

#TODO: pawel i wiktor tab, a takze nasze wykresy są tak podobne schematycznie, że może da rade z nich zrobić jakąś wspólną klase abstrakcyjną do dziedziczenia
#TODO: podajesz kopie wartosci liczby zebow a nie odniesienie. wiec sie nie zmienia wcale n wyj jak sie zmieni liczbe zebow. wykorzystalem juz istniejace update_animation_data zeby to naprawic, mozna zmienic jeszcze
#TODO: jak sie zmieni tu wartosci tak, ze wywali mi otwory poza zarys czy cos, to moje bledy tego nie lapią. Trzeba wysyłać dane innym po zmianie wartosci. Rozwiazlaem to tak, ze uzywam tej samej metody co do zmiany zakladki, tylko bez zmiany, bo ten sam index ktory jest podaje

class DataEdit(QWidget):
    wykresy_data_updated = Signal(int, dict)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout1 = QGridLayout()

#TODO: Uporządkować te dane w jakiś fany sposób :D
                    #z    ro    h    g  a1 a2 f1 f2 w1 w2 b  rg g  e  h obc.   l_k   -> obc. - obciążenie wejsciowe! , l_k -> liczba kół
        self.dane = [24, 4.8, 0.625, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 500, 2]
        self.luzy = Tolerancje()
        self.n_wejsciowe = 750
        self.omega = math.pi*self.n_wejsciowe/30
        self.tarcie_stali =0.00003
        self.dane_materialowe = DaneMaterialowe(self.dane[0])

        self.dane_all ={
            "z" : 24,
            "ro" : 4.8,
            "lam" : 0.625,
            "g" : 11,
            "Ra1" : 0,
            "Rf1": 0,
            "Rw1": 0,
            "Ra2": 0,
            "Rf2": 0,
            "Rw2": 0,
            "Rb" : 0,
            "Rg" : 0,
            "e" : 0,
            "h" : 0,
            "Mwej" : 500,
            "K" : 2,
            "Y1" : 2100000,
            "Y2" : 2100000,
            "v1" :0.3,
            "v2" :0.3,
            "b" : 17,
            "nwej" : 500,
            "nwyj" : 21,
            "t1" : 0.00001,
            "t2" : 0.00001,
            "l-ze" : 0.0000,
            "l-rg" : 0,
            "l-ri" : 0,
            "l-rr" : 0,
            "l-e" : 0
        }



        self.sily = None
        self.naprezenia = None
        self.refil_data()
        self.liczba_obciazonych_rolek = 0
        self.przyrost_kata = 360 / (self.dane[0] + 1)

        self.spin_z = DoubleSpinBox(self.dane[0],8,68,1)
        self.spin_z.lineEdit().setReadOnly(True)
        self.spin_ro = DoubleSpinBox(self.dane[1],3,8,0.05)
        self.spin_h = DoubleSpinBox(self.dane[2],0.5,0.99,0.01)
        self.spin_g = DoubleSpinBox(self.dane[3],5,14,0.02)
        self.spin_obc = DoubleSpinBox(self.dane[15], 500, 5000, 10)
        self.spin_l_k = DoubleSpinBox(self.dane[16], 1, 2, 1)
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
        layout_main.addWidget(self.luzy)

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

        self.obliczenia_sil()

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
        straty_mocy = [None] * self.liczba_obciazonych_rolek
        luzy = [None] * self.liczba_obciazonych_rolek
        Mk = self.dane[15]/self.dane[16]
        for a in range(self.liczba_obciazonych_rolek):
            i=a+1
            kat = i*self.przyrost_kata
            #reke=((self.dane[1]*(self.dane[0]+1)*math.pow((1-(2*self.dane[2]*math.cos(self.dane[0]*kat*0.0175))+math.pow(self.dane[2],2)),(3/2)))/(1-(self.dane[2]*(self.dane[0]+2)*(math.cos(self.dane[0]*kat*0.0175)))+(math.pow(self.dane[2],2)*(self.dane[0]+1)))-(self.dane[3]))
            reke = ((self.dane[1] * (self.dane[0] + 1) * math.pow(
                (1 - (2 * self.dane[2] * math.cos(kat * 0.0175)) + math.pow(self.dane[2], 2)),
                (3 / 2))) / (1 - (self.dane[2] * (self.dane[0] + 2) * (math.cos(kat * 0.0175))) + (
                        math.pow(self.dane[2], 2) * (self.dane[0] + 1))) - (self.dane[3]))
            teta=i*self.przyrost_kata
            x=math.sqrt((math.pow(self.dane[10],2))+(math.pow(self.dane[6],2))-(2*self.dane[10]*self.dane[6]*math.cos(teta * 0.0175)))
            beta = math.degrees(math.asin(self.dane[10]*math.sin(teta * 0.0175)/x))
            alfa[a]=90-beta
            sily[a]=(4*Mk*math.cos(alfa[a] * 0.0175))/(self.dane[6]*(self.dane[0]+1))
            #naprezenia[a]=math.sqrt((sily[a]*(reke+self.dane[3]))/(self.dane_materialowe.dane_materialowe[4]*math.pi*reke*self.dane[3]*(((1-math.pow(self.dane_materialowe.dane_materialowe[2],2))/(self.dane_materialowe.dane_materialowe[0])))+((1-math.pow(self.dane_materialowe.dane_materialowe[3],2))/(self.dane_materialowe.dane_materialowe[1]))))
            naprezenia[a]=math.sqrt((sily[a]*(reke+self.dane[3]))/((self.dane_materialowe.dane_materialowe[4]*3.1415*reke*self.dane[3])*(((1-math.pow(self.dane_materialowe.dane_materialowe[2],2))/(self.dane_materialowe.dane_materialowe[0]))+((1-math.pow(self.dane_materialowe.dane_materialowe[3],2))/(self.dane_materialowe.dane_materialowe[1])))))

            #Straty Mocy

            AIC = (math.sqrt(math.pow(self.dane[9],2)+math.pow((self.dane[5]+self.dane[3]),2)-2*self.dane[3]*(self.dane[5]+self.dane[3])*math.cos(kat*0.0175)))-self.dane[3]
            straty_mocy[a]= self.omega*(self.dane[8]/self.dane[13])*(((AIC/self.dane[3])+1)*self.tarcie_stali+(AIC/self.dane[3])*self.tarcie_stali)*sily[a]
            luzy[a]= 1+kat
        self.sily=sily
        self.naprezenia=naprezenia

        self.wykresy_data_updated.emit(self.dane[0], {
            "sily": sily,
            "naprezenia": naprezenia,
            "straty_mocy": straty_mocy,
            "luz_miedzyzebny": luzy,
        })


class Tab_Pawel(AbstractTab):
    anim_data_updated = Signal(dict)
    update_other_tabs = Signal()

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
        self.data.dane_materialowe.z = int(self.data.spin_z.value())
        self.data.dane_materialowe.obliczanie_predkosci_wyjsciowej()
        self.anim_data_updated.emit({"pawel": self.data.dane})
        self.update_other_tabs.emit()

    def send_data(self):
        return {"pawel": {
            "R_w1": self.data.dane[6],
            "R_f1": self.data.dane[5],
            "e": self.data.dane[13],
            "M": self.data.dane[15],
            "K": self.data.dane[16],
            "n_wej": self.data.dane_materialowe.dane_kinematyczne[0],
            "E_kola": self.data.dane_materialowe.dane_materialowe[0],
            "v_kola": self.data.dane_materialowe.dane_materialowe[2],
        }}
    
    def receive_data(self, new_data):
        ...


class DaneMaterialowe(QWidget):
    def __init__(self, liczba_z,):
        super().__init__()

        self.z = liczba_z
        #     Y1         Y2     v1 v2   B
        self.dane_materialowe = [210000.0, 210000.0, 0.3, 0.3, 50]
        #   nwej,nwyj  fzarysu frolki
        self.dane_kinematyczne = [500, 0, 0.00003, 0.00003]

        self.spin_Y1 = DoubleSpinBox(self.dane_materialowe[0], 100000, 500000, 10000)
        self.spin_Y2 = DoubleSpinBox(self.dane_materialowe[1], 100000, 500000, 10000)
        self.spin_P1 = DoubleSpinBox(self.dane_materialowe[2], 0.1, 0.7, 0.02)
        self.spin_P2 = DoubleSpinBox(self.dane_materialowe[3], 0.1, 0.7, 0.02)
        self.spin_B = DoubleSpinBox(self.dane_materialowe[4], 20, 100, 2)

        self.spin_nwej = DoubleSpinBox(self.dane_kinematyczne[0], 500, 5000, 10)
        self.spin_nwyj = QLabelD(self.dane_kinematyczne[1])
        self.spin_fzarysu = DoubleSpinBox(self.dane_kinematyczne[2], 0.00001, 0.0001, 0.00001)
        self.spin_frolki = DoubleSpinBox(self.dane_kinematyczne[3], 0.00001, 0.0001, 0.00001)

        self.spin_fzarysu.setDecimals(5)
        self.spin_frolki.setDecimals(5)


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
        layout.addWidget(QLabelD("DANE KINEMATYCZNE : "))
        layout.addWidget(QLabelD("Obroty wejsciowe :"))
        layout.addWidget(self.spin_nwej)
        self.obliczanie_predkosci_wyjsciowej()
        layout.addWidget(QLabelD("Obroty wyjsciowe :"))
        layout.addWidget(self.spin_nwyj)
        layout.addWidget(QLabelD("Współczynnik tarcia koła :"))
        layout.addWidget(self.spin_fzarysu)
        layout.addWidget(QLabelD("Współczynnik tarcia rolki :"))
        layout.addWidget(self.spin_frolki)



        # Zmiana w danych  :
        self.spin_Y1.valueChanged.connect(self.zmiana_danych)
        self.spin_Y2.valueChanged.connect(self.zmiana_danych)
        self.spin_P1.valueChanged.connect(self.zmiana_danych)
        self.spin_P2.valueChanged.connect(self.zmiana_danych)
        self.spin_B.valueChanged.connect(self.zmiana_danych)
        self.spin_nwej.valueChanged.connect(self.zmiana_danych)
        self.spin_fzarysu.valueChanged.connect(self.zmiana_danych)
        self.spin_frolki.valueChanged.connect(self.zmiana_danych)

        self.setLayout(layout)

    def zmiana_danych(self):
        self.dane_materialowe[0] = self.spin_Y1.value()
        self.dane_materialowe[1] = self.spin_Y2.value()
        self.dane_materialowe[2] = self.spin_P1.value()
        self.dane_materialowe[3] = self.spin_P2.value()
        self.dane_materialowe[4] = self.spin_B.value()

        self.dane_kinematyczne[0] = self.spin_nwej.value()
        self.dane_kinematyczne[2] = self.spin_fzarysu.value()
        self.dane_kinematyczne[3] = self.spin_frolki.value()

        self.obliczanie_predkosci_wyjsciowej()

    def obliczanie_predkosci_wyjsciowej(self):
        self.dane_kinematyczne[1] = self.dane_kinematyczne[0] / self.z
        self.spin_nwyj.setText(str(round(self.dane_kinematyczne[1])))


# Wprowadzenie danych dolerancji - karta

class Tolerancje(QWidget):
    def __init__(self):
        super().__init__()

        self.luzy = [0.0,0.0,0.0,0.0,0.0]
        self.rysunki = Rysunki_pomocnicze()
        main_layout = QVBoxLayout()

        layout = QVBoxLayout()
        layout.addWidget(QLabelD("LUZY :"))


        self.luzy_ze = DoubleSpinBox(self.luzy[0], -0.005, 0.005, 0.0001)
        self.luzy_rg = DoubleSpinBox(self.luzy[1], -0.005, 0.005, 0.0001)
        self.luzy_ri = DoubleSpinBox(self.luzy[2], -0.005, 0.005, 0.0001)
        self.luzy_rr = DoubleSpinBox(self.luzy[3], -0.005, 0.005, 0.0001)
        self.luzy_e = DoubleSpinBox(self.luzy[4], -0.005, 0.005, 0.0001)

        layout.addWidget(QLabelD("Luz ze:"))
        layout.addWidget(self.luzy_ze)
        layout.addWidget(QLabelD("Luz rg:"))
        layout.addWidget(self.luzy_rg)
        layout.addWidget(QLabelD("Luz ri:"))
        layout.addWidget(self.luzy_ri)
        layout.addWidget(QLabelD("Luz rr:"))
        layout.addWidget(self.luzy_rr)
        layout.addWidget(QLabelD("Luz e:"))
        layout.addWidget(self.luzy_e)

        

        main_layout.addLayout(layout)
        main_layout.addSpacing(50)
        main_layout.addWidget(self.rysunki)

        self.setLayout(main_layout)




class Rysunki_pomocnicze(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(QLabelD("RYSUNEK 1 :"))
        layout.addWidget(QLabelD("RYSUNEK 2 :"))
        layout.addWidget(QLabelD("RYSUNEK 3 :"))
        layout.addWidget(QLabelD("RYSUNEK 4 :"))
        layout.addWidget(QLabelD("RYSUNEK 5 :"))


        self.setLayout(layout)
