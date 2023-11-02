from PySide6.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QDoubleSpinBox, QPushButton, QHBoxLayout
from PySide6.QtGui import QPainter, QPixmap,Qt, QPolygon, QPen,QBrush
from PySide6.QtCore import QPoint, QSize
from pawlowe.wykresy import Wykresy
import math
import time
import threading

def rysowanie_tuleje(painter, mimosrod, pozycja_mimosrodu, scala, dane_wiktor, obecny_kat_obrotu):
    mimo_x, mimo_y = pozycja_mimosrodu
    liczba_tuleji = dane_wiktor["n"]
    R_wk = dane_wiktor["R_wk"]
    d_sw = dane_wiktor["d_sw"] * scala
    d_tul = dane_wiktor["d_tul"] * scala
    d_otw = dane_wiktor["d_otw"] * scala

    # TODO: tutaj inny kat. Trzeba go bedzie liczyc w animacji
    wyj_prz_x = mimosrod * math.cos(obecny_kat_obrotu * 0.0175)
    wyj_prz_y = mimosrod * math.sin(obecny_kat_obrotu * 0.0175)

    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * (i - 1)) / liczba_tuleji

        # rysowanie otworów
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        x_okj = (R_wk * math.sin(fi_kj) + mimo_x) * scala - d_otw / 2
        y_okj = (R_wk * math.cos(fi_kj) + mimo_y) * scala - d_otw / 2
        painter.drawEllipse(x_okj, y_okj, d_otw, d_otw)

        # rysowanie tuleji
        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        x_okj = (R_wk * math.sin(fi_kj) + mimo_x + wyj_prz_x) * scala - d_tul / 2
        y_okj = (R_wk * math.cos(fi_kj) + mimo_y + wyj_prz_y) * scala - d_tul / 2
        painter.drawEllipse(x_okj, y_okj, d_tul, d_tul)

        # rysowanie sworzni
        painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
        x_okj = (R_wk * math.sin(fi_kj) + mimo_x + wyj_prz_x) * scala - d_sw / 2
        y_okj = (R_wk * math.cos(fi_kj) + mimo_y + wyj_prz_y) * scala - d_sw / 2
        painter.drawEllipse(x_okj, y_okj, d_sw, d_sw)


class Animation_View(QWidget):
    def __init__(self, parent, dane):
        super().__init__(parent)
        main_layout = QVBoxLayout()
        # animation_controls = QHBoxLayout()
        self.start_animation_button = QPushButton("START ANIMACJI")
        self.start_animation_button.setCheckable(True)
        self.start_animation_button.clicked.connect(self.start_przycisk)
        # animation_controls.addWidget(self.start_animation_button)

        self.animacja = Animacja(dane)
        main_layout.addWidget(self.animacja)
        main_layout.addWidget(self.start_animation_button)
        self.setLayout(main_layout)

    def start_przycisk(self):
        if self.start_animation_button.text() == "START ANIMACJI":
            if self.animacja.status_animacji == 0:
                self.animacja.start_animacji()
                self.start_animation_button.setText("STOP ANIMACJI")
        else:
            self.start_animation_button.setText("START ANIMACJI")
            self.animacja.status_animacji = 0
    
    def update_animation_data(self, data):
        self.animacja.data = data['pawel'] if data.get('pawel') else self.animacja.data
        self.animacja.data_wiktor = data['wiktor'] if data.get('wiktor') else self.animacja.data_wiktor
        self.animacja.rysowanko()


class Animacja(QWidget):
    def __init__(self, data):
        super().__init__()

        self.setMinimumSize(640,640)
        self.data=data
        self.data_wiktor = None
        self.kat_=0
        self.kat_dorotacji = 0
        self.status_animacji = 0
        self.skok_kata = 0

        self.layout = QGridLayout()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #f0f0f0")

        self._size = QSize(self.width(), self.height())
        self.layout.addWidget(self.label)

        self.rysowanko()

    def rysowanko(self):
        pixmap = QPixmap(self._size)
        pixmap.fill("#f0f0f0")
        painter = QPainter(pixmap)
        pen = QPen(Qt.black,1)
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        painter.setPen(pen)
        points = QPolygon()
        self.data[0]=int(self.data[0])
        painter.translate(320,320)
        painter.rotate(self.kat_dorotacji)

        #skalowanie rysunku :
        scala = (self.data[1] * (self.data[0] + 1) * math.cos(0)) - (self.data[2] * self.data[1] * (math.cos((self.data[0] + 1) * 0))) - ((self.data[3] * ((math.cos(0) - (self.data[2] * math.cos((self.data[0] + 1) * 0))) / (math.sqrt(1 - (2 * self.data[2] * math.cos(self.data[0] * 0)) + (self.data[2] * self.data[2]))))))
        scala = (220/scala)

        przesuniecie_x = self.data[13]*math.cos(self.kat_* 0.0175)
        przesuniecie_y = self.data[13]*math.sin(self.kat_* 0.0175)

        # Rysowanie pierscienia okalającego :
        painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data[11] * scala * 2) + (self.data[3] * 4 * scala)))/2), -(((self.data[11] * scala * 2) + (self.data[3] * 4 * scala)))/2, ((self.data[11] * scala * 2) + (self.data[3] * 4 * scala)),((self.data[11] * scala * 2) + (self.data[3] * 4 * scala)))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data[11] * scala * 2)))/ 2),-(((self.data[11] * scala * 2))) / 2,((self.data[11] * scala * 2)),((self.data[11] * scala * 2)))
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))

        # rysowanie zarysu :
        for j in range(0,1440):
            i=j/4
            x = (self.data[1] * (self.data[0] + 1) * math.cos(i * 0.0175)) - (self.data[2] * self.data[1] * (math.cos((self.data[0] + 1) * i * 0.0175))) - ((self.data[3] * ((math.cos(i * 0.0175) - (self.data[2] * math.cos((self.data[0] + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * self.data[2] * math.cos(self.data[0] * i * 0.0175)) + (self.data[2] * self.data[2]))))))+przesuniecie_x
            y = (self.data[1] * (self.data[0] + 1) * math.sin(i * 0.0175)) - (self.data[2] * self.data[1] * (math.sin((self.data[0] + 1) * i * 0.0175))) - ((self.data[3] * ((math.sin(i * 0.0175) - (self.data[2] * math.sin((self.data[0] + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * self.data[2] * math.cos(self.data[0] * i * 0.0175)) + (self.data[2] * self.data[2]))))))+przesuniecie_y
            x=x*scala
            y=y*scala
            points.insert(j, QPoint(x, y))
        painter.drawPolygon(points)
        
        #Rysowanie otworow, tuleji
        if self.data_wiktor is not None:
            rysowanie_tuleje(painter, self.data[13], (przesuniecie_x, przesuniecie_y), scala, self.data_wiktor, self.kat_)

        #Rysowanie rolek :
        painter.setBrush(QBrush(Qt.blue,Qt.SolidPattern))
        painter.rotate(-self.kat_dorotacji)
        liczba_rolek = int(self.data[0])+1
        self.skok_kata = 360/liczba_rolek

        for i in range(liczba_rolek):
            x = self.data[11]*math.cos(i*self.skok_kata* 0.0175)*scala
            y = self.data[11] * math.sin(i * self.skok_kata * 0.0175) * scala
            painter.drawEllipse(x-(self.data[12]*scala),y-(self.data[12]*scala),self.data[12]*scala*2,self.data[12]*scala*2)

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

        self.setLayout(self.layout)
        self.label.setPixmap(pixmap)
        painter.end()

    def start_animacji(self):
        self.status_animacji = 1
        def animacja_thread():
            while self.status_animacji==1:
                time.sleep(0.04)
                self.kat_+=self.skok_kata
                self.kat_dorotacji = -((360/(self.data[0]+1))*(self.kat_/360))
                self.rysowanko()
                if self.kat_>= 360*(self.data[0]+1):
                     self.kat_ = 0
                     self.kat_dorotacji = 0
        threading.Thread(target=animacja_thread).start()
