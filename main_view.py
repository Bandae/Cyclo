from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QSlider
from PySide2.QtGui import QPainter, QPixmap, QPolygon, QPen,QBrush, QPainterPath
from PySide2.QtCore import QPoint, QSize, Qt, Signal, QRect
import math
import time
import threading

# TODO: możliwe że wywala program czasem przy aktualizacji danych które są używane przez animację. Może Przerwać ją, wczytać, zacząć znowu
# moze ustawic ścieżki do rysowania, i zmieniac je tylko jak sa zmienione dane.
# jest też opcja że to kwestia sprzętowa, na lapku mi wywalało, na kompie nie widzę problemu w sumie
# WAZNE TODO: juz wiem. jak sie nie obroci ukladu odniesienia, tylko przesunie, to otwory sie dobrze przechodza

# dopoki nie powroci do glownego programu po event.clear() to nie skonczy wykonywac animacji. Moze byc potrzebne zmuszenei uzytkowanika do zatrzymania animacji zeby cokolwiek zrobic jak sie te bledy nie poprawaia :(
def tworz_zarys_kola(z, ro, h, g, scala, pozycja_mimosrodu, data_wiktor,ktory):
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
        x = x * scala
        y = y * scala
        # new_x = ((x - pozycja_mimosrodu[0]) * math.cos(kat_obrotu) + (y - pozycja_mimosrodu[1]) * math.sin(kat_obrotu)) * scala + pozycja_mimosrodu[0] * scala
        # new_y = (-(x - pozycja_mimosrodu[0]) * math.sin(kat_obrotu) + (y - pozycja_mimosrodu[1]) * math.cos(kat_obrotu)) * scala + pozycja_mimosrodu[1] * scala
        points.insert(j, QPoint(x, y))
    zarys.addPolygon(points)
    
    if data_wiktor is not None:
        zarys = wytnij_otwory(zarys, scala, pozycja_mimosrodu, data_wiktor, ktory)
    
    return zarys

def wytnij_otwory(zarys, scala, pozycja_mimosrodu, dane_wiktor, ktory):
    liczba_tuleji = dane_wiktor["n"]
    R_wk = dane_wiktor["R_wk"]
    d_otw = dane_wiktor["d_otw"] * scala
    d_tul = dane_wiktor['d_tul']*scala
    mimo_x, mimo_y = pozycja_mimosrodu

    otwory = QPainterPath()
    if ktory==1:
        for i in range(liczba_tuleji):
            fi_kj = (2 * math.pi * i) / liczba_tuleji
            x_okj = (R_wk * math.cos(fi_kj) + mimo_x) * scala - d_otw / 2
            y_okj = (R_wk * math.sin(fi_kj) + mimo_y) * scala - d_otw / 2
            otwory.addEllipse(x_okj, y_okj, d_otw, d_otw)
    elif ktory==2:
        for i in range(liczba_tuleji):
            fi_kj = (2 * math.pi * i) / liczba_tuleji
            x_okj = (R_wk * math.cos(fi_kj) - mimo_x) * scala - d_otw / 2
            y_okj = (R_wk * math.sin(fi_kj) - mimo_y) * scala - d_otw / 2
            otwory.addEllipse(x_okj, y_okj, d_otw, d_otw)
    else :
        r=((R_wk*2*scala)+(d_tul*(100/87)))
        otwory.addEllipse(-(r/2), -(r/2), r, r)

    return zarys.subtracted(otwory)

def rysowanie_tuleje(painter, scala, dane_wiktor, kolory):
    liczba_tuleji = dane_wiktor["n"]
    R_wk = dane_wiktor["R_wk"]
    d_sw = dane_wiktor["d_sw"] * scala
    d_tul = dane_wiktor["d_tul"] * scala

    tuleje = QPainterPath()
    sworznie = QPainterPath()

    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * (i - 1)) / liczba_tuleji

        # rysowanie tuleji
        x_okj = (R_wk * math.cos(fi_kj)) * scala - d_tul / 2
        y_okj = (R_wk * math.sin(fi_kj)) * scala - d_tul / 2
        tuleje.addEllipse(x_okj, y_okj, d_tul, d_tul)

        # rysowanie sworzni
        x_okj = (R_wk * math.cos(fi_kj)) * scala - d_sw / 2
        y_okj = (R_wk * math.sin(fi_kj)) * scala - d_sw / 2
        sworznie.addEllipse(x_okj, y_okj, d_sw, d_sw)
    painter.setBrush(QBrush(kolory["tuleje"], Qt.SolidPattern))
    painter.drawPath(tuleje)
    painter.setBrush(QBrush(kolory["sworznie"], Qt.SolidPattern))
    painter.drawPath(sworznie)


class AnimationView(QWidget):
    def __init__(self, parent, dane):
        super().__init__(parent)
        self.animacja = Animacja(self, dane)
        self.start_event = threading.Event()

        main_layout = QVBoxLayout()
        animation_controls = QGridLayout()
        bcgrd = QWidget(self)
        bcgrd.setMaximumHeight(60)
        self.start_animation_button = QPushButton("START ANIMACJI", bcgrd)
        self.restet_animacji = QPushButton("POZYCJA POCZĄTKOWA", bcgrd)
        self.slider = QSlider(Qt.Horizontal, bcgrd)
        self.slider.setMaximum(360)
        self.slider.valueChanged.connect(self.setAngle)
        self.animacja.animation_tick.connect(self.updateSlider)
        self.angle_label = QLabel(bcgrd)
        self.start_animation_button.setMaximumSize(160, 20)
        self.start_animation_button.clicked.connect(self.startPrzycisk)
        self.restet_animacji.setMaximumSize(160, 20)
        self.restet_animacji.clicked.connect(self.resetAnimacji)

        bcgrd.setLayout(animation_controls)
        animation_controls.addWidget(self.start_animation_button, 1, 0)
        animation_controls.addWidget(self.restet_animacji, 1, 1)
        animation_controls.addWidget(self.slider, 0, 0, 1, 2)
        animation_controls.addWidget(self.angle_label, 0, 3)
        main_layout.addWidget(self.animacja)
        main_layout.addWidget(bcgrd)
        main_layout.setAlignment(Qt.AlignHCenter)
        animation_controls.setAlignment(Qt.AlignHCenter)
        main_layout.setContentsMargins(80, 20, 80, 20)
        self.setLayout(main_layout)

    def startPrzycisk(self):
        if self.start_animation_button.text() == "START ANIMACJI":
            self.start_animation_button.setText("STOP ANIMACJI")
            self.start_event.set()
            time.sleep(0.04)
            threading.Thread(target=self.animacja.startAnimacji, args=(self.start_event,)).start()
        else:
            self.start_animation_button.setText("START ANIMACJI")
            self.start_event.clear()
            time.sleep(0.1)
    
    def updateAnimationData(self, data):
        if data.get('pawel'):
            self.animacja.data = data['pawel']
        if data.get('wiktor', False) == False:
            self.animacja.data_wiktor = None
        elif data.get('wiktor'):
            self.animacja.data_wiktor = data['wiktor']
        self.animacja.rysowanko()

    def resetAnimacji(self):
        self.start_animation_button.setText("START ANIMACJI")
        self.start_event.clear()
        self.angle_label.setText("0" + "\u00B0")
        self.slider.setValue(0)
        self.animacja.setAngle(0, reset=True)

    def setAngle(self, slider_value):
        if self.start_event.is_set():
            return
        self.angle_label.setText(str(slider_value) + "\u00B0")
        self.animacja.setAngle(slider_value)
    
    def updateSlider(self, value):
        if not self.start_event.is_set():
            return
        self.angle_label.setText(str(-round(value)) + "\u00B0")
        self.slider.setValue(-value)


class Animacja(QLabel):
    animation_tick = Signal(float)

    SLATE = "#283E39"
    METAL_LIGHT = "#529AB7"
    METAL_DARK = "#12242B"
    WHITE = "#FFFFFF"
    GRAY_LIGHT = "#B4B4B4"
    GRAY = "#323434"
    GRAY_DARK = "#92929"
    PASTEL_BLUE = '#ADD8E6'
    PASTEL_BLUE2 = '#BDE4E6'
    def __init__(self, parent, data):
        super().__init__(parent)

        self.setMinimumSize(750,750)
        self.data = data
        self.data_wiktor = None
        self.kat_ = 0
        self.kat_2 = 180*(self.data["z"]+1)
        self.kat_dorotacji = 0
        self.kat_dorotacji2 = -((self.kat_2+180)/(self.data["z"]+1))
        self.skok_kata = 0

        self.layout = QGridLayout()
        # self.label = QLabel(self)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #f0f0f0")

        self._size = QSize(self.width(), self.height())
        # self.layout.addWidget(self.label)
        # self.setLayout(self.layout)
        self.rysowanko()

    def rysowanko(self):
        pixmap = QPixmap(self._size)
        pixmap.fill("#f0f0f0")
        painter = QPainter(pixmap)
        pen = QPen(Qt.black,1)
        painter.setPen(pen)
        painter.translate(350,350)

        self.data["z"]=int(self.data["z"])
        liczba_rolek = self.data["z"]+1
        self.skok_kata = 360/liczba_rolek

        #skalowanie rysunku :
        paint_area = 700
        max_size = (self.data["Rg"] * 2) + (self.data["g"] * 4)
        scala = paint_area / max_size

        przesuniecie_x = self.data["e"]*math.cos(self.kat_* 0.0175)
        przesuniecie_y = self.data["e"]*math.sin(self.kat_* 0.0175)

        # Rysowanie pierscienia okalającego :
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))/2), -(((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))/2, ((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)),((self.data["Rg"] * scala * 2) + (self.data["g"] * 4 * scala)))
        painter.setBrush(QBrush(self.WHITE, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * scala * 2)))/ 2),-(((self.data["Rg"] * scala * 2))) / 2,((self.data["Rg"] * scala * 2)),((self.data["Rg"] * scala * 2)))

        # rysowanie zarysu :
        zarys = tworz_zarys_kola(self.data["z"], self.data["ro"], self.data["lam"], self.data["g"], scala, (przesuniecie_x, przesuniecie_y), self.data_wiktor,1)
        zarys2 = tworz_zarys_kola(self.data["z"], self.data["ro"], self.data["lam"], self.data["g"], scala, (przesuniecie_x, przesuniecie_y), self.data_wiktor,2)
        zarys3 = tworz_zarys_kola(self.data["z"], self.data["ro"], self.data["lam"], self.data["g"], scala, (przesuniecie_x, przesuniecie_y), self.data_wiktor, 3)

        painter.setBrush(QBrush(self.PASTEL_BLUE2, Qt.SolidPattern))

        painter.rotate(self.kat_dorotacji)
        if self.data["K"] == 2:
            painter.drawPath(zarys3)
        painter.rotate(-self.kat_dorotacji+self.kat_dorotacji2)
        if self.data["K"] == 2:
            painter.drawPath(zarys2)
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        painter.drawPath(zarys)

        if self.data_wiktor is not None:
            rysowanie_tuleje(painter, scala, self.data_wiktor, {"tuleje": self.METAL_DARK,"sworznie": self.SLATE})
        painter.rotate(-self.kat_dorotacji2)

        #Rysowanie rolek :
        painter.setBrush(QBrush(self.GRAY_LIGHT, Qt.SolidPattern))
        for i in range(liczba_rolek):
            x = self.data["Rg"] * math.cos(i * self.skok_kata * 0.0175) * scala
            y = self.data["Rg"] * math.sin(i * self.skok_kata * 0.0175) * scala
            painter.drawEllipse(x-(self.data["g"]*scala),y-(self.data["g"]*scala),self.data["g"]*scala*2,self.data["g"]*scala*2)

        #Rysowanie Wałka

        #painter.setBrush(QBrush(Qt.yellow))
        #painter.drawEllipse(-(10*scala),-(10*scala),20*scala,20*scala)

        # Rysowanie punktu mimośrodu
        # pen2 = QPen(Qt.red, 3)
        # painter.setPen(pen2)
        # painter.drawPoint(0, 0)

        # if self.data_wiktor is not None:
        #     pr = self.data_wiktor["R_wk"] * scala
        #     painter.drawArc(-pr, -pr, pr*2, pr*2, 0, 16 * 360)

        #Rysowanie punktu "C"
        #xp = self.data[8]*math.cos(self.kat_dorotacji* 0.0175)
        #yp = self.data[8]*math.sin(self.kat_dorotacji* 0.0175)
        #painter.drawPoint(xp,yp)

        self.setPixmap(pixmap)
        painter.end()

    def setAngle(self, new_angle, reset=False):
        if reset:
            self.kat_ = 0
        else:
            self.kat_ = self.kat_ // 360 + new_angle
        self.kat_dorotacji = -((360/(self.data["z"]+1))*(self.kat_/360))
        self.kat_2 = self.kat_ + 180*(self.data["z"]+1)
        self.kat_dorotacji2 = -((self.kat_2+180)/(self.data["z"]+1))
        self.rysowanko()

    def startAnimacji(self, event):
        while event.is_set():
            time.sleep(0.04)
            self.kat_ += self.skok_kata
            self.kat_2 += self.skok_kata
            self.kat_dorotacji = -(self.kat_/(self.data["z"]+1))
            self.kat_dorotacji2 = -((self.kat_2+180)/(self.data["z"]+1))
            self.rysowanko()
            if self.kat_ >= 360*(self.data["z"]+1):
                self.kat_ = 0
                self.kat_2 = 180*(self.data["z"]+1)
                self.kat_dorotacji = 0
            self.animation_tick.emit(self.kat_dorotacji)
