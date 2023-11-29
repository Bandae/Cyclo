from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QSlider
from PySide2.QtGui import QPainter, QPixmap, QPolygon, QPen,QBrush, QPainterPath
from PySide2.QtCore import QPoint, QSize, Qt, Signal
from pawlowe.wykresy import Wykresy
import math
import time
import threading

# TODO: możliwe że wywala program czasem przy aktualizacji danych które są używane przez animację. Może Przerwać ją, wczytać, zacząć znowu
# moze ustawic ścieżki do rysowania, i zmieniac je tylko jak sa zmienione dane.
# jest też opcja że to kwestia sprzętowa, na lapku mi wywalało, na kompie nie widzę problemu w sumie
# WAZNE TODO: juz wiem. jak sie nie obroci ukladu odniesienia, tylko przesunie, to otwory sie dobrze przechodza

# dopoki nie powroci do glownego programu po event.clear() to nie skonczy wykonywac animacji. Moze byc potrzebne zmuszenei uzytkowanika do zatrzymania animacji zeby cokolwiek zrobic jak sie te bledy nie poprawaia :(
def tworz_zarys_kola(z, ro, h, g, scala, pozycja_mimosrodu, data_wiktor):
    zarys = QPainterPath()
    points = QPolygon()
    for j in range(0,1440):
        i=j/4
        #wzory bednarczyka
        # y = (ro * z + ro) * math.cos(i * 0.0175) - ro * h * math.cos(((ro * z + ro) / ro) * i * 0.0175) - g * ((math.cos(i * 0.0175) - h * math.cos((z + 1) * i * 0.0175)) / ((1 - 2 * h * math.cos(z * i * 0.0175) + h**2) ** 0.5)) + pozycja_mimosrodu[1]
        # x = (ro * z + ro) * math.sin(i * 0.0175) - ro * h * math.sin(((ro * z + ro) / ro) * i * 0.0175) - g * ((math.sin(i * 0.0175) - h * math.sin((z + 1) * i * 0.0175)) / ((1 - 2 * h * math.cos(z * i * 0.0175) + h**2) ** 0.5)) + pozycja_mimosrodu[0]
        # wzory Pawla
        x = (ro * (z + 1) * math.cos(i * 0.0175)) - (h * ro * (math.cos((z + 1) * i * 0.0175))) - ((g * ((math.cos(i * 0.0175) - (h * math.cos((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h)))))) + pozycja_mimosrodu[0]
        y = (ro * (z + 1) * math.sin(i * 0.0175)) - (h * ro * (math.sin((z + 1) * i * 0.0175))) - ((g * ((math.sin(i * 0.0175) - (h * math.sin((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h)))))) + pozycja_mimosrodu[1]
        x=x*scala
        y=y*scala
        points.insert(j, QPoint(x, y))
    zarys.addPolygon(points)
    
    if data_wiktor is not None:
        zarys = wytnij_otwory(zarys, scala, pozycja_mimosrodu, data_wiktor)
    
    return zarys

def wytnij_otwory(zarys, scala, pozycja_mimosrodu, dane_wiktor):
    liczba_tuleji = dane_wiktor["n"]
    R_wk = dane_wiktor["R_wk"]
    d_otw = dane_wiktor["d_otw"] * scala
    mimo_x, mimo_y = pozycja_mimosrodu

    otwory = QPainterPath()
    # - 180 * 0.0175 * nr_kola
    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * (i - 1)) / liczba_tuleji
        x_okj = (R_wk * math.cos(fi_kj) + mimo_x) * scala - d_otw / 2
        y_okj = (R_wk * math.sin(fi_kj) + mimo_y) * scala - d_otw / 2
        otwory.addEllipse(x_okj, y_okj, d_otw, d_otw)
    return zarys.subtracted(otwory)

def rysowanie_tuleje(painter, pozycja_mimosrodu, scala, dane_wiktor, kolory):
    mimo_x, mimo_y = pozycja_mimosrodu
    liczba_tuleji = dane_wiktor["n"]
    R_wk = dane_wiktor["R_wk"]
    d_sw = dane_wiktor["d_sw"] * scala
    d_tul = dane_wiktor["d_tul"] * scala

    tuleje = QPainterPath()
    sworznie = QPainterPath()

    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * (i - 1)) / liczba_tuleji

        # rysowanie tuleji
        x_okj = (R_wk * math.cos(fi_kj) + mimo_x*2) * scala - d_tul / 2
        y_okj = (R_wk * math.sin(fi_kj) + mimo_y*2) * scala - d_tul / 2
        tuleje.addEllipse(x_okj, y_okj, d_tul, d_tul)

        # rysowanie sworzni
        x_okj = (R_wk * math.cos(fi_kj) + mimo_x*2) * scala - d_sw / 2
        y_okj = (R_wk * math.sin(fi_kj) + mimo_y*2) * scala - d_sw / 2
        sworznie.addEllipse(x_okj, y_okj, d_sw, d_sw)
    painter.setBrush(QBrush(kolory["tuleje"], Qt.SolidPattern))
    painter.drawPath(tuleje)
    painter.setBrush(QBrush(kolory["sworznie"], Qt.SolidPattern))
    painter.drawPath(sworznie)


class Animation_View(QWidget):
    def __init__(self, parent, dane):
        super().__init__(parent)
        self.animacja = Animacja(dane)
        self.start_event = threading.Event()

        main_layout = QVBoxLayout()
        animation_controls = QGridLayout()
        self.start_animation_button = QPushButton("START ANIMACJI")
        self.restet_animacji = QPushButton("POZYCJA POCZĄTKOWA")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximumWidth(400)
        self.slider.setMaximum(360)
        self.slider.valueChanged.connect(self.set_angle)
        self.animacja.animation_tick.connect(self.update_slider)
        self.angle_label = QLabel()
        self.start_animation_button.setCheckable(True)
        self.start_animation_button.clicked.connect(self.start_przycisk)
        self.restet_animacji.clicked.connect(self.reset_animacji)

        animation_controls.addWidget(self.start_animation_button, 1, 0)
        animation_controls.addWidget(self.restet_animacji, 1, 1)
        animation_controls.addWidget(self.slider, 0, 0)
        animation_controls.addWidget(self.angle_label, 0, 1)
        main_layout.addWidget(self.animacja)
        main_layout.addLayout(animation_controls)
        main_layout.setContentsMargins(80, 20, 80, 20)
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
        if data.get('pawel'):
            self.animacja.data = data['pawel']
        if data.get('wiktor', False) == False:
            self.animacja.data_wiktor = None
        elif data.get('wiktor'):
            self.animacja.data_wiktor = data['wiktor']
        self.animacja.rysowanko()

    def reset_animacji(self):
        self.start_animation_button.setText("START ANIMACJI")
        self.start_event.clear()
        self.angle_label.setText("0" + "\u00B0")
        self.slider.setValue(0)
        self.animacja.kat_ = 0
        self.animacja.kat_dorotacji = 0

    def set_angle(self, slider_value):
        if self.start_event.is_set():
            return
        self.angle_label.setText(str(slider_value) + "\u00B0")
        self.animacja.set_angle(slider_value)
    
    def update_slider(self, value):
        if not self.start_event.is_set():
            return
        self.angle_label.setText(str(-round(value)) + "\u00B0")
        self.slider.setValue(-value)


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
        self.data["z"]=int(self.data["z"])
        painter.translate(320,320)
        # painter.rotate(90)

        #skalowanie rysunku :
        scala = (self.data["ro"] * (self.data["z"] + 1) * math.cos(0)) - (self.data["lam"] * self.data["ro"] * (math.cos((self.data["z"] + 1) * 0))) - ((self.data["g"] * ((math.cos(0) - (self.data["lam"] * math.cos((self.data["z"] + 1) * 0))) / (math.sqrt(1 - (2 * self.data["lam"] * math.cos(self.data["z"] * 0)) + (self.data["lam"] * self.data["lam"]))))))
        scala = (220/scala)

        przesuniecie_x = self.data["e"]*math.cos(self.kat_* 0.0175)
        przesuniecie_y = self.data["e"]*math.sin(self.kat_* 0.0175)

        przesuniecie_x2 = self.data["e"]*math.cos((self.kat_+180)* 0.0175)
        przesuniecie_y2 = self.data["e"]*math.sin((self.kat_+180)* 0.0175)
        kat_dorotacji2 = -((360/(self.data["z"]+1))*((self.kat_+180)/360))

        # Rysowanie pierscienia okalającego :
        painter.setBrush(QBrush(self.GRAY_DARK, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))/2), -(((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))/2, ((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)),((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))
        painter.setBrush(QBrush(self.WHITE, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * scala * 2)))/ 2),-(((self.data["Rg"] * scala * 2))) / 2,((self.data["Rg"] * scala * 2)),((self.data["Rg"] * scala * 2)))

        # rysowanie zarysu :
        zarys1 = tworz_zarys_kola(self.data["z"], self.data["ro"], self.data["lam"], self.data["g"], scala, (przesuniecie_x, przesuniecie_y), self.data_wiktor)
        zarys2 = tworz_zarys_kola(self.data["z"], self.data["ro"], self.data["lam"], self.data["g"], scala, (przesuniecie_x2, przesuniecie_y2), self.data_wiktor)

        painter.setBrush(QBrush(self.METAL_LIGHT, Qt.SolidPattern))
        painter.rotate(self.kat_dorotacji)
        painter.drawPath(zarys1)
        painter.rotate(kat_dorotacji2-self.kat_dorotacji)
        painter.drawPath(zarys2)
        if self.data_wiktor is not None:
            rysowanie_tuleje(painter, (przesuniecie_x2, przesuniecie_y2), scala, self.data_wiktor, {"tuleje": self.METAL_DARK,"sworznie": self.SLATE})

        painter.rotate(-kat_dorotacji2)

        #Rysowanie rolek :
        painter.setBrush(QBrush(self.METAL_DARK, Qt.SolidPattern))
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

    def set_angle(self, new_angle):
        self.kat_ = self.kat_ // 360 + new_angle
        self.kat_dorotacji = -((360/(self.data["z"]+1))*(self.kat_/360))
        self.rysowanko()

    def start_animacji(self, event):
        while event.is_set():
            time.sleep(0.04)
            self.kat_ += self.skok_kata
            self.kat_dorotacji = -((360/(self.data["z"]+1))*(self.kat_/360))
            self.rysowanko()
            if self.kat_ >= 360*(self.data["z"]+1):
                self.kat_ = 0
                self.kat_dorotacji = 0
            self.animation_tick.emit(self.kat_dorotacji)
