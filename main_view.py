from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QHBoxLayout
from PySide2.QtGui import QPainter, QPixmap, QPolygon, QPen,QBrush, QPainterPath
from PySide2.QtCore import QPoint, QSize, Qt, Signal
from pawlowe.wykresy import Wykresy
import math
import time
import threading

# TODO: możliwe że wywala program czasem przy aktualizacji danych które są używane przez animację. Może Przerwać ją, wczytać, zacząć znowu
# moze ustawic ścieżki do rysowania, i zmieniac je tylko jak sa zmienione dane.
# dopoki nie powroci do glownego programu po event.clear() to nie skonczy wykonywac animacji. Moze byc potrzebne zmuszenei uzytkowanika do zatrzymania animacji zeby cokolwiek zrobic jak sie te bledy nie poprawaia :(

def rysowanie_tuleje(painter, zarys, mimosrod, pozycja_mimosrodu, scala, dane_wiktor, obecny_kat_obrotu, kolory):
    mimo_x, mimo_y = pozycja_mimosrodu
    liczba_tuleji = dane_wiktor["n"]
    R_wk = dane_wiktor["R_wk"]
    d_sw = dane_wiktor["d_sw"] * scala
    d_tul = dane_wiktor["d_tul"] * scala
    d_otw = dane_wiktor["d_otw"] * scala

    # TODO: tutaj inny kat. Trzeba go bedzie liczyc w animacji
    wyj_prz_x = mimosrod * math.cos(obecny_kat_obrotu * 0.0175)
    wyj_prz_y = mimosrod * math.sin(obecny_kat_obrotu * 0.0175)

    otwory = QPainterPath()
    tuleje = QPainterPath()
    sworznie = QPainterPath()

    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * (i - 1)) / liczba_tuleji

        # rysowanie otworów
        x_okj = (R_wk * math.sin(fi_kj) + mimo_x) * scala - d_otw / 2
        y_okj = (R_wk * math.cos(fi_kj) + mimo_y) * scala - d_otw / 2
        otwory.addEllipse(x_okj, y_okj, d_otw, d_otw)

        # rysowanie tuleji
        x_okj = (R_wk * math.sin(fi_kj) + mimo_x + wyj_prz_x) * scala - d_tul / 2
        y_okj = (R_wk * math.cos(fi_kj) + mimo_y + wyj_prz_y) * scala - d_tul / 2
        tuleje.addEllipse(x_okj, y_okj, d_tul, d_tul)

        # rysowanie sworzni
        x_okj = (R_wk * math.sin(fi_kj) + mimo_x + wyj_prz_x) * scala - d_sw / 2
        y_okj = (R_wk * math.cos(fi_kj) + mimo_y + wyj_prz_y) * scala - d_sw / 2
        sworznie.addEllipse(x_okj, y_okj, d_sw, d_sw)
    painter.setBrush(QBrush(kolory["tuleje"], Qt.SolidPattern))
    painter.drawPath(tuleje)
    painter.setBrush(QBrush(kolory["sworznie"], Qt.SolidPattern))
    painter.drawPath(sworznie)
    return zarys.subtracted(otwory)

class Animation_View(QWidget):
    def __init__(self, parent, dane):
        super().__init__(parent)
        self.animacja = Animacja(dane)
        self.start_event = threading.Event()

        main_layout = QVBoxLayout()
        animation_controls = QHBoxLayout()
        self.start_animation_button = QPushButton("START ANIMACJI")
        self.restet_animacji = QPushButton("POZYCJA POCZĄTKOWA")
        self.start_animation_button.setCheckable(True)
        self.start_animation_button.clicked.connect(self.start_przycisk)
        self.restet_animacji.clicked.connect(self.reset_animacji)

        animation_controls.addWidget(self.start_animation_button)
        animation_controls.addWidget(self.restet_animacji)
        main_layout.addWidget(self.animacja)
        main_layout.addLayout(animation_controls)
        self.setLayout(main_layout)

    def start_przycisk(self):
        if self.start_animation_button.text() == "START ANIMACJI":
            self.start_animation_button.setText("STOP ANIMACJI")
            self.start_event.set()
            time.sleep(0.04)
            threading.Thread(target=self.animacja.start_animacji, args=(self.start_event,)).start()
        else:
            self.start_animation_button.setText("START ANIMACJI")
            self.start_event.clear()
            time.sleep(0.1)
    
    def update_animation_data(self, data):
        # TODO: ta proba wywalenia bledow przy zmianie danych nie dość, że chyba nie dziala, to psuje wydajność animacji, nawet jak jest nieuzywane - ???
        # animation_active = self.start_event.is_set()
        # if animation_active:
        #     self.start_przycisk()
        if data.get('pawel'):
            self.animacja.data = data['pawel']
        if data.get('wiktor', False) == False:
            self.animacja.data_wiktor = None
        elif data.get('wiktor'):
            self.animacja.data_wiktor = data['wiktor']
        self.animacja.rysowanko()
        # if animation_active:
        #     self.start_przycisk()

    def reset_animacji(self, animacja):
        # animation_active = self.start_event.is_set()
        # if animation_active:
        #     self.start_przycisk()
        self.start_animation_button.setText("START ANIMACJI")
        self.start_event.clear()
        self.animacja.kat_ = 0
        self.animacja.kat_dorotacji = 0
        # self.animacja.rysowanko()
        # self.animacja.animation_tick.emit(self.animacja.kat_dorotacji)
        # if animation_active:
        #     self.start_przycisk()


class Animacja(QWidget):
    animation_tick = Signal(float)

    SLATE = "#283E39"
    METAL_LIGHT = "#529AB7"
    METAL_DARK = "#12242B"
    WHITE = "#FFFFFF"
    GRAY_LIGHT = "#787D7D"
    GRAY = "#323434"
    GRAY_DARK = "#92929"
    def __init__(self, data):
        super().__init__()

        self.setMinimumSize(640,640)
        self.data=data
        print(int(self.data["z"]))
        self.data_wiktor = None
        self.kat_=0
        self.kat_dorotacji = 0
        self.skok_kata = 0

        self.layout = QGridLayout()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #f0f0f0")

        self._size = QSize(self.width(), self.height())
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.rysowanko()

    def rysowanko(self):
        pixmap = QPixmap(self._size)
        pixmap.fill("#f0f0f0")
        painter = QPainter(pixmap)
        pen = QPen(Qt.black,1)
        painter.setPen(pen)
        points = QPolygon()
        self.data["z"]=int(self.data["z"])
        painter.translate(320,320)
        painter.rotate(self.kat_dorotacji)

        #skalowanie rysunku :
        scala = (self.data["ro"] * (self.data["z"] + 1) * math.cos(0)) - (self.data["lam"] * self.data["ro"] * (math.cos((self.data["z"] + 1) * 0))) - ((self.data["g"] * ((math.cos(0) - (self.data["lam"] * math.cos((self.data["z"] + 1) * 0))) / (math.sqrt(1 - (2 * self.data["lam"] * math.cos(self.data["z"] * 0)) + (self.data["lam"] * self.data["lam"]))))))
        scala = (220/scala)

        przesuniecie_x = self.data["e"]*math.cos(self.kat_* 0.0175)
        przesuniecie_y = self.data["e"]*math.sin(self.kat_* 0.0175)

        # Rysowanie pierscienia okalającego :
        painter.setBrush(QBrush(self.GRAY_DARK, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))/2), -(((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))/2, ((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)),((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))
        painter.setBrush(QBrush(self.WHITE, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * scala * 2)))/ 2),-(((self.data["Rg"] * scala * 2))) / 2,((self.data["Rg"] * scala * 2)),((self.data["Rg"] * scala * 2)))

        # rysowanie zarysu :
        zarys = QPainterPath()
        for j in range(0,1440):
            i=j/4
            x = (self.data["ro"] * (self.data["z"] + 1) * math.cos(i * 0.0175)) - (self.data["lam"] * self.data["ro"] * (math.cos((self.data["z"] + 1) * i * 0.0175))) - ((self.data["g"] * ((math.cos(i * 0.0175) - (self.data["lam"] * math.cos((self.data["z"] + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * self.data["lam"] * math.cos(self.data["z"] * i * 0.0175)) + (self.data["lam"] * self.data["lam"]))))))+przesuniecie_x
            y = (self.data["ro"] * (self.data["z"] + 1) * math.sin(i * 0.0175)) - (self.data["lam"] * self.data["ro"] * (math.sin((self.data["z"] + 1) * i * 0.0175))) - ((self.data["g"] * ((math.sin(i * 0.0175) - (self.data["lam"] * math.sin((self.data["z"] + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * self.data["lam"] * math.cos(self.data["z"] * i * 0.0175)) + (self.data["lam"] * self.data["lam"]))))))+przesuniecie_y
            x=x*scala
            y=y*scala
            points.insert(j, QPoint(x, y))
        zarys.addPolygon(points)
        
        #Rysowanie otworow, tuleji
        if self.data_wiktor is not None:
            zarys = rysowanie_tuleje(painter, zarys, self.data["e"], (przesuniecie_x, przesuniecie_y), scala, self.data_wiktor, self.kat_, {"tuleje": self.METAL_DARK,"sworznie": self.SLATE})

        painter.setBrush(QBrush(self.METAL_LIGHT, Qt.SolidPattern))
        painter.drawPath(zarys)

        #Rysowanie rolek :
        painter.setBrush(QBrush(self.METAL_DARK, Qt.SolidPattern))
        painter.rotate(-self.kat_dorotacji)
        liczba_rolek = int(self.data["z"])+1
        self.skok_kata = 360/liczba_rolek

        for i in range(liczba_rolek):
            x = self.data["Rg"]*math.cos(i*self.skok_kata* 0.0175)*scala
            y = self.data["Rg"] * math.sin(i * self.skok_kata * 0.0175) * scala
            painter.drawEllipse(x-(self.data["g"]*scala),y-(self.data["g"]*scala),self.data["g"]*scala*2,self.data["g"]*scala*2)

        #Rysowanie Wałka

        #painter.setBrush(QBrush(Qt.yellow))
        #painter.drawEllipse(-(10*scala),-(10*scala),20*scala,20*scala)

        #Rysowanie punktu mimośrodu
        #pen2 = QPen(Qt.red, 3)
        #painter.setPen(pen2)
        #painter.drawPoint(przesuniecie_x,przesuniecie_y)

        #Rysowanie punktu "C"
        #xp = self.data[8]*math.cos(self.kat_dorotacji* 0.0175)
        #yp = self.data[8]*math.sin(self.kat_dorotacji* 0.0175)
        #painter.drawPoint(xp,yp)

        self.label.setPixmap(pixmap)
        painter.end()

    def start_animacji(self, event):
        # TODO: ta opcja z co 4 troche brzydka ale poprawia wydajność
        # i = 0
        while event.is_set():
            time.sleep(0.04)
            # i += 0.04
            self.kat_ += self.skok_kata
            self.kat_dorotacji = -((360/(self.data["z"]+1))*(self.kat_/360))
            self.rysowanko()
            if self.kat_ >= 360*(self.data["z"]+1):
                self.kat_ = 0
                self.kat_dorotacji = 0
            self.animation_tick.emit(self.kat_dorotacji)
            # if i >= 0.16:
            #     i = 0
            #     self.animation_tick.emit(self.kat_dorotacji)
