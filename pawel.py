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

        self.dane_all ={
            "z" : 24,       "ro" : 4.8,
            "lam" : 0.625,  "g" : 11,
            "Ra1" : 0,      "Rf1": 0,
            "Rw1": 0,       "Ra2": 0,
            "Rf2": 0,       "Rw2": 0,
            "Rb" : 0,       "Rg" : 0,
            "e" : 0,        "h" : 0,
            "Mwej" : 500,   "K" : 2,
            "E1" : 2100000, "E2" : 2100000,
            "v1" :0.3,      "v2" :0.3,
            "b" : 17,       "nwej" : 500,
            "nwyj" : 21,    "t1" : 0.00001,
            "t2" : 0.00001, "l-ze" : 0.0000,
            "l-rg" : 0,     "l-ri" : 0,
            "l-rr" : 0,     "l-e" : 0
        }

        self.luzy = Tolerancje(self.dane_all)
        self.dane_materialowe = DaneMaterialowe(self.dane_all["z"],self.dane_all)

        self.refil_data()
        self.liczba_obciazonych_rolek = 0
        self.przyrost_kata = 360 / (self.dane_all["z"] + 1)

        self.spin_z = DoubleSpinBox(self.dane_all["z"],8,68,1)
        self.spin_z.lineEdit().setReadOnly(True)
        self.spin_ro = DoubleSpinBox(self.dane_all["ro"],3,8,0.05)
        self.spin_h = DoubleSpinBox(self.dane_all["lam"],0.5,0.99,0.01)
        self.spin_g = DoubleSpinBox(self.dane_all["g"],5,14,0.02)
        self.spin_obc = DoubleSpinBox(self.dane_all["Mwej"], 500, 5000, 10)
        self.spin_l_k = DoubleSpinBox(self.dane_all["K"], 1, 2, 1)
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

        self.data_labels = {
            'Ra1': QLabelD(str(round(self.dane_all["Ra1"], 2))),
            'Rf1': QLabelD(str(round(self.dane_all["Rf1"], 2))),
            'Rw1': QLabelD(str(round(self.dane_all["Rw1"], 2))),
            'Ra2': QLabelD(str(round(self.dane_all["Ra2"], 2))),
            'Rf2': QLabelD(str(round(self.dane_all["Rf2"], 2))),
            'Rw2': QLabelD(str(round(self.dane_all["Rw2"], 2))),
            'Rb': QLabelD(str(round(self.dane_all["Rb"], 2))),
            'Rg': QLabelD(str(round(self.dane_all["Rg"], 2))),
            'g': QLabelD(str(round(self.dane_all["g"], 2))),
            'e': QLabelD(str(round(self.dane_all["e"], 2))),
            'h': QLabelD(str(round(self.dane_all["h"], 2)))
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
        z=self.dane_all["z"]
        ro=self.dane_all["ro"]
        lam=self.dane_all["lam"]
        g=self.dane_all["g"]
        self.dane_all["Ra1"] = ro*(z+1+lam)-g
        self.dane_all["Rf1"] = ro*(z+1-lam)-g
        self.dane_all["Rw1"] = ro*lam*z
        self.dane_all["Ra2"] = ro*(z+1)-g
        self.dane_all["Rf2"] = ro*(z+1+(2*lam))-g
        self.dane_all["Rw2"] = ro*lam*(z+1)
        self.dane_all["Rb"] = ro*z
        self.dane_all["Rg"] = ro*(z+1)
        self.dane_all["g"] = g
        self.dane_all["e"] = ro*lam
        self.dane_all["h"] = 2*self.dane_all["e"]

        self.obliczenia_sil()

    def refili_labels(self):
        for text, qlabel in self.data_labels.items():
            qlabel.setText(str(round(self.dane_all[text], 2)))

    def z_changed(self):
        self.dane_all["z"] = self.spin_z.value()
        self.dane_all["ro"] = self.spin_ro.value()
        self.dane_all["lam"] = self.spin_h.value()
        self.dane_all["g"] = self.spin_g.value()
        self.dane_all["Mwej"] = self.spin_obc.value()
        self.dane_all["K"] = self.spin_l_k.value()

        h_min = (self.dane_all["z"]-1)/(2*self.dane_all["z"]+1)
        self.spin_h.setMinimum(h_min)

        self.refil_data()
        self.refili_labels()
        self.obliczenia_sil()

    def obliczenia_sil(self,kat_glowny=0):
        if self.dane_all["z"]%2==0:
            self.liczba_obciazonych_rolek = int(self.dane_all["z"]/2)
        else :
            self.liczba_obciazonych_rolek = int((self.dane_all["z"]+1)/2)-1
        self.przyrost_kata = 360/(self.dane_all["z"]+1)
        
        sily = [None]*self.liczba_obciazonych_rolek
        alfa = [None] * self.liczba_obciazonych_rolek
        naprezenia = [None] * self.liczba_obciazonych_rolek
        straty_mocy = [None] * self.liczba_obciazonych_rolek
        luzy = [None] * self.liczba_obciazonych_rolek
        Mk = self.dane_all["Mwej"]/self.dane_all["K"]
        for a in range(self.liczba_obciazonych_rolek):
            i=a+1
            kat = kat_glowny*self.przyrost_kata
            #reke=((self.dane_all["ro"]*(self.dane_all["z"]+1)*math.pow((1-(2*self.dane_all["lam"]*math.cos(self.dane_all["z"]*kat*0.0175))+math.pow(self.dane_all["lam"],2)),(3/2)))/(1-(self.dane_all["lam"]*(self.dane_all["z"]+2)*(math.cos(self.dane_all["z"]*kat*0.0175)))+(math.pow(self.dane_all["lam"],2)*(self.dane_all["z"]+1)))-(self.dane_all["g"]))
            reke = ((self.dane_all["ro"] * (self.dane_all["z"] + 1) * math.pow(
                (1 - (2 * self.dane_all["lam"] * math.cos(kat * 0.0175)) + math.pow(self.dane_all["lam"], 2)),
                (3 / 2))) / (1 - (self.dane_all["lam"] * (self.dane_all["z"] + 2) * (math.cos(kat * 0.0175))) + (
                        math.pow(self.dane_all["lam"], 2) * (self.dane_all["z"] + 1))) - (self.dane_all["g"]))
            teta=i*self.przyrost_kata
            x=math.sqrt((math.pow(self.dane_all["Rb"],2))+(math.pow(self.dane_all["Rw1"],2))-(2*self.dane_all["Rb"]*self.dane_all["Rw1"]*math.cos(teta * 0.0175)))
            beta = math.degrees(math.asin(self.dane_all["Rb"]*math.sin(teta * 0.0175)/x))
            alfa[a]=90-beta
            sily[a]=(4*Mk*math.cos(alfa[a] * 0.0175))/(self.dane_all["Rw1"]*(self.dane_all["z"]+1))
            #naprezenia[a]=math.sqrt((sily[a]*(reke+self.dane_all["g"]))/(self.dane_all["b"]*math.pi*reke*self.dane_all["g"]*(((1-math.pow(self.dane_all["v1"],2))/(self.dane_all["E1"])))+((1-math.pow(self.dane_all["v1"],2))/(self.dane_all["E2"]))))
            naprezenia[a]=math.sqrt((sily[a]*(reke+self.dane_all["g"]))/((self.dane_all["b"]*3.1415*reke*self.dane_all["g"])*(((1-math.pow(self.dane_all["v1"],2))/(self.dane_all["E1"]))+((1-math.pow(self.dane_all["v2"],2))/(self.dane_all["E2"])))))

            #Straty Mocy

            AIC = (math.sqrt(math.pow(self.dane_all["Rw2"],2)+math.pow((self.dane_all["Rf1"]+self.dane_all["g"]),2)-2*self.dane_all["g"]*(self.dane_all["Rf1"]+self.dane_all["g"])*math.cos(kat*0.0175)))-self.dane_all["g"]
            straty_mocy[a]= ((math.pi*self.dane_all["nwej"])/30)*(self.dane_all["Rf2"]/self.dane_all["e"])*(((AIC/self.dane_all["g"])+1)*self.dane_all["t1"]+(AIC/self.dane_all["g"])*self.dane_all["t2"])*sily[a]
            luzy[a]= 1+kat
        self.sily=sily
        self.naprezenia=naprezenia

        self.wykresy_data_updated.emit(self.dane_all["z"], {
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
        self.data.dane_materialowe.obliczanie_predkosci_wyjsciowej(self.data.dane_all)
        self.anim_data_updated.emit({"pawel": self.data.dane_all})
        self.update_other_tabs.emit()

    def send_data(self):
        return {"pawel": {
            "R_w1": self.data.dane_all["Rw1"],
            "R_f1": self.data.dane_all["Rf1"],
            "e": self.data.dane_all["e"],
            "M": self.data.dane_all["Mwej"],
            "K": self.data.dane_all["K"],
            "n_wej": self.data.dane_materialowe.dane_kinematyczne[0],
            "E_kola": self.data.dane_materialowe.dane_materialowe[0],
            "v_kola": self.data.dane_materialowe.dane_materialowe[2],
        }}
    
    def receive_data(self, new_data):
        ...


class DaneMaterialowe(QWidget):
    def __init__(self, liczba_z,dane_all):
        super().__init__()

        self.z = liczba_z

        self.spin_Y1 = DoubleSpinBox(dane_all["E1"], 100000, 500000, 10000)
        self.spin_Y2 = DoubleSpinBox(dane_all["E2"], 100000, 500000, 10000)
        self.spin_P1 = DoubleSpinBox(dane_all["v1"], 0.1, 0.7, 0.02)
        self.spin_P2 = DoubleSpinBox(dane_all["v2"], 0.1, 0.7, 0.02)
        self.spin_B = DoubleSpinBox(dane_all["b"], 20, 100, 2)

        self.spin_nwej = DoubleSpinBox(dane_all["nwej"], 500, 5000, 10)
        self.spin_nwyj = QLabelD(dane_all["nwyj"])
        self.spin_fzarysu = DoubleSpinBox(dane_all["t1"], 0.00001, 0.0001, 0.00001)
        self.spin_frolki = DoubleSpinBox(dane_all["t2"], 0.00001, 0.0001, 0.00001)

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
        layout.addSpacing(80)
        layout.addWidget(QLabelD("DANE KINEMATYCZNE : "))
        layout.addWidget(QLabelD("Obroty wejsciowe :"))
        layout.addWidget(self.spin_nwej)
        self.obliczanie_predkosci_wyjsciowej(dane_all)
        layout.addWidget(QLabelD("Obroty wyjsciowe :"))
        layout.addWidget(self.spin_nwyj)
        layout.addWidget(QLabelD("Współczynnik tarcia koła :"))
        layout.addWidget(self.spin_fzarysu)
        layout.addWidget(QLabelD("Współczynnik tarcia rolki :"))
        layout.addWidget(self.spin_frolki)




        # Zmiana w danych  :
        self.spin_Y1.valueChanged.connect(self.zmiana_danych(dane_all))
        self.spin_Y2.valueChanged.connect(self.zmiana_danych(dane_all))
        self.spin_P1.valueChanged.connect(self.zmiana_danych(dane_all))
        self.spin_P2.valueChanged.connect(self.zmiana_danych(dane_all))
        self.spin_B.valueChanged.connect(self.zmiana_danych(dane_all))
        self.spin_nwej.valueChanged.connect(self.zmiana_danych(dane_all))
        self.spin_fzarysu.valueChanged.connect(self.zmiana_danych(dane_all))
        self.spin_frolki.valueChanged.connect(self.zmiana_danych(dane_all))

        self.setLayout(layout)

    def zmiana_danych(self,dane_all):
        dane_all["E1"] = self.spin_Y1.value()
        dane_all["E2"] = self.spin_Y2.value()
        dane_all["v1"] = self.spin_P1.value()
        dane_all["v2"] = self.spin_P2.value()
        dane_all["b"] = self.spin_B.value()

        dane_all["nwej"] = self.spin_nwej.value()
        dane_all["t1"] = self.spin_fzarysu.value()
        dane_all["t2"] = self.spin_frolki.value()

        self.obliczanie_predkosci_wyjsciowej(dane_all)

    def obliczanie_predkosci_wyjsciowej(self,dane_all):
        dane_all["nwyj"] = dane_all["nwej"] / self.z
        self.spin_nwyj.setText(str(round(dane_all["nwyj"])))


# Wprowadzenie danych dolerancji - karta

class Tolerancje(QWidget):
    def __init__(self,dane_all):
        super().__init__()

        self.rysunki = Rysunki_pomocnicze()
        main_layout = QVBoxLayout()

        layout = QVBoxLayout()
        layout.addWidget(QLabelD("LUZY :"))

        self.luzy_ze = DoubleSpinBox(dane_all["l-ze"], -0.005, 0.005, 0.0001, 4)
        self.luzy_rg = DoubleSpinBox(dane_all["l-rg"], -0.005, 0.005, 0.0001, 4)
        self.luzy_ri = DoubleSpinBox(dane_all["l-ri"], -0.005, 0.005, 0.0001, 4)
        self.luzy_rr = DoubleSpinBox(dane_all["l-rr"], -0.005, 0.005, 0.0001, 4)
        self.luzy_e = DoubleSpinBox(dane_all["l-e"], -0.005, 0.005, 0.0001, 4)



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
