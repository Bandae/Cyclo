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
            "Rb" : 0,       "Rb2":0,
            "Rg" : 0,       "sr":0,
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
        self.spin_ro = DoubleSpinBox(self.dane_all["ro"],1,8,0.05)
        self.spin_h = DoubleSpinBox(self.dane_all["lam"],0.5,0.99,0.01)
        self.spin_g = DoubleSpinBox(self.dane_all["g"],3,14,0.02)
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
        self.dane_all["Rb2"] = z+g+self.dane_all["Rf1"]
        self.dane_all["Rg"] = ro*(z+1)
        self.dane_all["e"] = ro*lam
        self.dane_all["h"] = 2*self.dane_all["e"]
        self.dane_all["sr"] = (2*g)+(2*self.dane_all['Rb2'])
        self.obliczenia_sil()

    def refili_labels(self):
        for text, qlabel in self.data_labels.items():
            qlabel.setText(str(round(self.dane_all[text], 2)))

        self.luzy.rysunki.sr.setText(str(self.dane_all['sr']))

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

        self.liczba_obciazonych_rolek = int(self.dane_all["z"])+1


        F_max = (1000*4*(self.dane_all['Mwej']/self.dane_all['K']))/(self.dane_all['Rw1']*(self.dane_all['z']+1))

        al_ki = [None] * self.liczba_obciazonych_rolek
        al_si = [None] * self.liczba_obciazonych_rolek
        hi = [None] * self.liczba_obciazonych_rolek
        Fx = [None] * self.liczba_obciazonych_rolek
        Fy = [None] * self.liczba_obciazonych_rolek
        sily = [None] * self.liczba_obciazonych_rolek
        naprezenia = [None] * self.liczba_obciazonych_rolek
        straty_mocy = [None] * self.liczba_obciazonych_rolek
        luzy = [None] * self.liczba_obciazonych_rolek
        reke = [None] * self.liczba_obciazonych_rolek
        AIC = [None] * self.liczba_obciazonych_rolek




        Mk = self.dane_all["Mwej"]/self.dane_all["K"]
        for i in range(self.liczba_obciazonych_rolek):

            #NOWE

            #SILY
            al_ki[i] = (2*math.pi*i)/(self.dane_all['z']+1) + kat_glowny
            al_si[i] = (math.pi/2)-(math.fabs(math.atan((self.dane_all['Rb2']*math.sin(al_ki[i]))/((self.dane_all['Rw1']+self.dane_all['e'])-(self.dane_all['Rb2']*math.cos(al_ki[i]))))))
            hi[i] = self.dane_all['Rw1'] * math.cos(al_si[i])
            Fx[i] = F_max * (hi[i] / self.dane_all['Rw1']) * math.cos(al_si[i])
            Fy[i] = F_max * (hi[i] / self.dane_all['Rw1']) * math.sin(al_si[i])
            sily[i] = math.sqrt(math.pow(Fx[i],2)+math.pow(Fy[i],2))

            #NACISKI
            reke[i] = (self.dane_all['ro'] * (self.dane_all['z'] + 1) * ((1 - 2 * self.dane_all['lam'] * math.cos(self.dane_all['z'] * al_ki[i]) + (self.dane_all['lam']**2))**1.5) / (1 - self.dane_all['lam'] * (self.dane_all['z'] + 2) * math.cos(self.dane_all['z'] * al_ki[i]) + ((self.dane_all['lam'])**2) * (self.dane_all['z'] + 1))) - self.dane_all['g']
            naprezenia[i] = math.sqrt((sily[i]*math.fabs(self.dane_all['g']+reke[i]))/((self.dane_all['g']*math.fabs(reke[i])*self.dane_all['b'])*(((1-self.dane_all['v1'])/self.dane_all['E1'])+((1-self.dane_all['v2'])/self.dane_all['E2']))*math.pi))

            #STRATY_MOCY
            AIC[i]= ((self.dane_all['Rw2']**2+(self.dane_all['Ra2']+self.dane_all['g'])**2-2*self.dane_all['Rw2']*(self.dane_all['Ra2']+self.dane_all['g'])*math.cos(reke[i]))**0.5)-self.dane_all['g']
            straty_mocy[i] = (math.pi*(self.dane_all['nwej']/30))*(self.dane_all['e']/self.dane_all['Rw1'])*(((naprezenia[i]/self.dane_all['g'])+1)*self.dane_all['t1']+(naprezenia[i]/self.dane_all['g'])*self.dane_all['t2'])*sily[i]

            #LUZY MIEDZYZEBNE:
            x_ze=(self.dane_all['Rw1']+self.dane_all['ro'])*math.sin(al_ki[i])-self.dane_all['e']*math.sin(((self.dane_all['Rw1']+self.dane_all['ro'])/self.dane_all['ro'])*al_ki[i])-(self.dane_all['g']+self.dane_all['l-ze'])*((math.sin(al_ki[i])-self.dane_all['lam']*math.sin((self.dane_all['z']+1)*al_ki[i]))/((1-2*self.dane_all['lam']*math.cos(self.dane_all['z']*al_ki[i])+self.dane_all['lam']**2)**0.5))
            y_ze=(self.dane_all['Rw1']+self.dane_all['ro'])*math.cos(al_ki[i])-self.dane_all['e']*math.cos(((self.dane_all['Rw1']+self.dane_all['ro'])/self.dane_all['ro'])*al_ki[i])-(self.dane_all['g']+self.dane_all['l-ze'])*((math.cos(al_ki[i])-self.dane_all['lam']*math.cos((self.dane_all['z']+1)*al_ki[i]))/((1-2*self.dane_all['lam']*math.cos(self.dane_all['z']*al_ki[i])+self.dane_all['lam']**2)**0.5))
            x_ozri=(self.dane_all['Rb2']+self.dane_all['l-rg'])*math.sin(al_ki[i]+self.dane_all['l-ri'])
            y_ozri=(self.dane_all['Rb2']+self.dane_all['l-rg'])*math.cos(al_ki[i]+self.dane_all['l-ri'])-(self.dane_all['e']+self.dane_all['l-e'])
            luzy[i]=((((x_ozri-x_ze)**2)+((y_ozri-y_ze)**2))**0.5)-(self.dane_all['g'])


            # STARE
            #kat = kat_glowny*self.przyrost_kata
            #reke=((self.dane_all["ro"]*(self.dane_all["z"]+1)*math.pow((1-(2*self.dane_all["lam"]*math.cos(self.dane_all["z"]*kat*0.0175))+math.pow(self.dane_all["lam"],2)),(3/2)))/(1-(self.dane_all["lam"]*(self.dane_all["z"]+2)*(math.cos(self.dane_all["z"]*kat*0.0175)))+(math.pow(self.dane_all["lam"],2)*(self.dane_all["z"]+1)))-(self.dane_all["g"]))
            #reke = ((self.dane_all["ro"] * (self.dane_all["z"] + 1) * math.pow(
            #    (1 - (2 * self.dane_all["lam"] * math.cos(kat * 0.0175)) + math.pow(self.dane_all["lam"], 2)),
            #    (3 / 2))) / (1 - (self.dane_all["lam"] * (self.dane_all["z"] + 2) * (math.cos(kat * 0.0175))) + (
            #            math.pow(self.dane_all["lam"], 2) * (self.dane_all["z"] + 1))) - (self.dane_all["g"]))
            #teta=i*self.przyrost_kata
            #x=math.sqrt((math.pow(self.dane_all["Rb"],2))+(math.pow(self.dane_all["Rw1"],2))-(2*self.dane_all["Rb"]*self.dane_all["Rw1"]*math.cos(teta * 0.0175)))
            #beta = math.degrees(math.asin(self.dane_all["Rb"]*math.sin(teta * 0.0175)/x))
            #al_ki[i]=90-beta
            #sily[a]=(4*Mk*math.cos(alfa[a] * 0.0175))/(self.dane_all["Rw1"]*(self.dane_all["z"]+1))
            #naprezenia[a]=math.sqrt((sily[a]*(reke+self.dane_all["g"]))/(self.dane_all["b"]*math.pi*reke*self.dane_all["g"]*(((1-math.pow(self.dane_all["v1"],2))/(self.dane_all["E1"])))+((1-math.pow(self.dane_all["v1"],2))/(self.dane_all["E2"]))))
            #naprezenia[a]=math.sqrt((sily[i]*(reke+self.dane_all["g"]))/((self.dane_all["b"]*3.1415*reke*self.dane_all["g"])*(((1-math.pow(self.dane_all["v1"],2))/(self.dane_all["E1"]))+((1-math.pow(self.dane_all["v2"],2))/(self.dane_all["E2"])))))

            #Straty Mocy

            #AIC = (math.sqrt(math.pow(self.dane_all["Rw2"],2)+math.pow((self.dane_all["Rf1"]+self.dane_all["g"]),2)-2*self.dane_all["g"]*(self.dane_all["Rf1"]+self.dane_all["g"])*math.cos(kat*0.0175)))-self.dane_all["g"]
            #straty_mocy[a]= ((math.pi*self.dane_all["nwej"])/30)*(self.dane_all["Rf2"]/self.dane_all["e"])*(((AIC/self.dane_all["g"])+1)*self.dane_all["t1"]+(AIC/self.dane_all["g"])*self.dane_all["t2"])*sily[i]
            #luzy[a]= 1+kat

        self.wykresy_data_updated.emit(self.dane_all["z"], {
            "sily": sily,
            "naprezenia": naprezenia,
            "straty_mocy": straty_mocy,
            "luz_miedzyzebny": luzy,
        })

    def copyDataToInputs(self, new_input_data):
        self.spin_z.setValue(new_input_data["z"])
        self.spin_ro.setValue(new_input_data["ro"])
        self.spin_h.setValue(new_input_data["lam"])
        self.spin_g.setValue(new_input_data["g"])
        self.spin_obc.setValue(new_input_data["Mwej"])
        self.spin_l_k.setValue(new_input_data["K"])

        self.z_changed()
        self.dane_all = new_input_data


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

    def sendData(self):
        return {"pawel": {
            "R_w1": self.data.dane_all["Rw1"],
            "R_f1": self.data.dane_all["Rf1"],
            "e": self.data.dane_all["e"],
            "M": self.data.dane_all["Mwej"],
            "K": self.data.dane_all["K"],
            "n_wej": self.data.dane_all["nwej"],
            "E_kola": self.data.dane_all["E1"],
            "v_kola": self.data.dane_all["v1"],
        }}
    
    def receiveData(self, new_data):
        ...
    
    def saveData(self):
        self.data.z_changed()
        return {
            "data_pawel": self.data.dane_all,
        }

    def loadData(self, new_data):
        if new_data is None:
            return
        dane = new_data.get("data_pawel")
        self.data.copyDataToInputs(dane)
        self.data.dane_materialowe.copyDataToInputs(dane)
        self.data.dane_all = dane
        self.data.dane_materialowe.zmiana_danych(dane)

    def reportData(self):
        def table_row(cell1, cell2, cell3):
            a = "{\\trowd \\trgaph10 \\cellx5000 \\cellx7000 \\cellx8000 \\pard\\intbl "
            b = "\\cell\\pard\\intbl "
            return a + str(cell1) + b + str(cell2) + b + str(cell3) + " \\cell\\row}"

        text = "{\\pard\\qc\\f0\\fs44 Dane Zarysu : \\line\\par}"
        text += table_row("Srednica zewnętrzna", round(self.data.dane_all['sr'],2), "mm")
        text += table_row("Liczba ząbów", round(self.data.dane_all['z']), "")
        text += table_row("Promień koła obtaczającego", round(self.data.dane_all['ro'],2), "mm")
        text += table_row("Promień Krzywizny", round(self.data.dane_all['lam'],2), "mm")
        text += table_row("Promień rolki",round( self.data.dane_all['g'],2), "mm")
        text += table_row("Promień koła wierzchołkowego Ra1", round(self.data.dane_all['Ra1'],2), "mm")
        text += table_row("Promień koła stóp Rf1", round(self.data.dane_all['Rf1'],2), "mm")
        text += table_row("Promień koła tocznego Rw1", round(self.data.dane_all['Rw1'],2), "mm")
        text += table_row("Promień koła wierzchołkowego Ra2", round(self.data.dane_all['Ra2'],2), "mm")
        text += table_row("Promień koła stóp Rf2", round(self.data.dane_all['Rf2'],2), "mm")
        text += table_row("Promień koła tocznego Rw2", round(self.data.dane_all['Rw2'],2), "mm")
        text += table_row("Promień koła zasadniczego Rb1", round(self.data.dane_all['Rb'],2), "mm")
        text += table_row("Promień koła zasadniczego Rb2", round(self.data.dane_all['Rb2'],2), "mm")
        text += table_row("Promień rozmieszczenia rolki Rg", round(self.data.dane_all['Rg'],2), "mm")
        text += table_row("Mimośród", round(self.data.dane_all['e'],2), "mm")
        text += table_row("Wysokość zęba", round(self.data.dane_all['h'],2), "mm")
        text += table_row("Promień rolki", round(self.data.dane_all['K'],2), "mm")
        text += table_row("Szerokość kół", round(self.data.dane_all['b'],2), "mm")

        text += "{\\pard\\qc\\f0\\fs44 Dane Materiałowe : \\line\\par}"

        text += table_row("Moduł Yonga 1", round(self.data.dane_all['E1'],2), "")
        text += table_row("Moduł Yonga 2", round(self.data.dane_all['E2'],2), "")
        text += table_row("Współczynnik poissona 1", round(self.data.dane_all['v1'],2), "")
        text += table_row("Współczynnik poissona 2", round(self.data.dane_all['v2'],2), "")

        text += "{\\pard\\qc\\f0\\fs44 Dane Kinematyczne : \\line\\par}"
        text += table_row("Moment wyjsciowy", round(self.data.dane_all['Mwej'],2), "Nm")
        text += table_row("Obroty na wejściu", round(self.data.dane_all['nwej'],2), "n/min")
        text += table_row("Obroty na wyjsciu", round(self.data.dane_all['nwyj'],2), "n/min")
        text += table_row("Współczynnik tarcia 1", round(self.data.dane_all['t1'],2), "")
        text += table_row("Współczynnik tarcia 2", round(self.data.dane_all['t2'],2), "")

        text += "{\\pard\\qc\\f0\\fs44 Tolerancje : \\line\\par}"
        text += table_row("Tolerancja l-ze", round(self.data.dane_all['l-ze'],5), "mm")
        text += table_row("Tolerancja l-rg", round(self.data.dane_all['l-rg'],5), "mm")
        text += table_row("Tolerancja l-ri", round(self.data.dane_all['l-ri'],5), "mm")
        text += table_row("Tolerancja l-rr", round(self.data.dane_all['l-rr'],5), "mm")
        text += table_row("Tolerancja l-e", round(self.data.dane_all['l-e'],5), "mm")

        return text


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
        self.spin_fzarysu = DoubleSpinBox(dane_all["t1"], 0.00001, 0.0001, 0.00001, 5)
        self.spin_frolki = DoubleSpinBox(dane_all["t2"], 0.00001, 0.0001, 0.00001, 5)

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
        layout.addWidget(QLabelD("Prędkość obrotowa wej :"))
        layout.addWidget(self.spin_nwej)
        self.obliczanie_predkosci_wyjsciowej(dane_all)
        layout.addWidget(QLabelD("Prędkość obrotowa wyj :"))
        layout.addWidget(self.spin_nwyj)
        layout.addWidget(QLabelD("Współczynnik tarcia koła :"))
        layout.addWidget(self.spin_fzarysu)
        layout.addWidget(QLabelD("Współczynnik tarcia rolki :"))
        layout.addWidget(self.spin_frolki)

        # Zmiana w danych  :
        self.spin_Y1.valueChanged.connect(lambda: self.zmiana_danych(dane_all))
        self.spin_Y2.valueChanged.connect(lambda: self.zmiana_danych(dane_all))
        self.spin_P1.valueChanged.connect(lambda: self.zmiana_danych(dane_all))
        self.spin_P2.valueChanged.connect(lambda: self.zmiana_danych(dane_all))
        self.spin_B.valueChanged.connect(lambda: self.zmiana_danych(dane_all))
        self.spin_nwej.valueChanged.connect(lambda: self.zmiana_danych(dane_all))
        self.spin_fzarysu.valueChanged.connect(lambda: self.zmiana_danych(dane_all))
        self.spin_frolki.valueChanged.connect(lambda: self.zmiana_danych(dane_all))

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
    
    def copyDataToInputs(self, new_input_data):
        self.spin_Y1.setValue(new_input_data["E1"])
        self.spin_Y2.setValue(new_input_data["E2"])
        self.spin_P1.setValue(new_input_data["v1"])
        self.spin_P2.setValue(new_input_data["v2"])
        self.spin_B.setValue(new_input_data["b"])
        self.spin_nwej.setValue(new_input_data["nwej"])
        self.spin_fzarysu.setValue(new_input_data["t1"])
        self.spin_frolki.setValue(new_input_data["t2"])


# Wprowadzenie danych dolerancji - karta

class Tolerancje(QWidget):
    def __init__(self,dane_all):
        super().__init__()

        self.rysunki = Rysunki_pomocnicze(dane_all['sr'])
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
    def __init__(self,sr):
        super().__init__()

        layout = QVBoxLayout()
        self.sr = QLabelD(sr)
        layout.addWidget(QLabelD("RYSUNEK 1 :"))
        layout.addWidget(QLabelD("RYSUNEK 2 :"))
        layout.addWidget(QLabelD("RYSUNEK 3 :"))
        layout.addWidget(QLabelD("ŚREDNICA ZEWNĘTRZNA"))
        layout.addWidget(self.sr)


        self.setLayout(layout)

