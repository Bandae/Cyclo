import math
import threading
import time
from PySide2 import QtCore
from PySide2.QtCore import QPoint, Qt, Signal
from PySide2.QtGui import QPainter, QPixmap, QPolygon, QPen,QBrush, QPainterPath, QResizeEvent
from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QSlider

# TODO: możliwe że wystarczy wysłać sygnał z rysowania i połączyć z metodą w głównym wątku z flagą Qt::QueuedConnection zamiast tego Invoker
# TODO: skok kąta zmienia się przy liczbie zębów. Więc dla niektoych liczb zębów, self.kat_ może sie zdarzyć nie taki jak trzeba jak sie zmienia poza animacją.
# reset animacji to naprawia od razu, ale nie jej start. jest to kwestia kumulacji błędów, bo jak lece od 24 do 10 to sie zepsuje, ale jak zresetuje na 11 i zejde do 10 to już nie.
# narazie ustawiam reset jeśli było zmienione przełożenie/liczba zębów. Inny pomysł mam, żeby zmienić self.kat_ do najbliższego podzielnego przez skok kąta, to powinno działać

def tworz_zarys_kola(z, ro, h, g, scala):
    zarys = QPainterPath()
    points = QPolygon()
    for j in range(0,720):
        i=j/2
        x = (ro * (z + 1) * math.cos(i * 0.0175)) - (h * ro * (math.cos((z + 1) * i * 0.0175))) - ((g * ((math.cos(i * 0.0175) - (h * math.cos((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
        y = (ro * (z + 1) * math.sin(i * 0.0175)) - (h * ro * (math.sin((z + 1) * i * 0.0175))) - ((g * ((math.sin(i * 0.0175) - (h * math.sin((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
        points.insert(j, QPoint(x*scala, y*scala))
    zarys.addPolygon(points)
    
    return zarys

def wytnij_otwory(zarys, scala, dane_wiktor, obrot_poczatkowy):
    liczba_tuleji = dane_wiktor["n"]
    R_wt = dane_wiktor["R_wt"]
    d_otw = dane_wiktor["d_otw"] * scala

    otwory = QPainterPath()
    
    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * i) / liczba_tuleji
        x_okj = (R_wt * math.cos(fi_kj-obrot_poczatkowy*0.0175)) * scala - d_otw / 2
        y_okj = (R_wt * math.sin(fi_kj-obrot_poczatkowy*0.0175)) * scala - d_otw / 2
        otwory.addEllipse(x_okj, y_okj, d_otw, d_otw)

    return zarys.subtracted(otwory)

def rysowanie_tuleje(painter, scala, dane_wiktor, kolory):
    liczba_tuleji = dane_wiktor["n"]
    R_wt = dane_wiktor["R_wt"]
    d_sw = dane_wiktor["d_sw"] * scala
    d_tul = dane_wiktor["d_tul"] * scala

    tuleje = QPainterPath()
    sworznie = QPainterPath()

    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * i) / liczba_tuleji
        x_okj = (R_wt * math.cos(fi_kj)) * scala
        y_okj = (R_wt * math.sin(fi_kj)) * scala

        tuleje.addEllipse(x_okj - d_tul / 2, y_okj - d_tul / 2, d_tul, d_tul)
        sworznie.addEllipse(x_okj - d_sw / 2, y_okj - d_sw / 2, d_sw, d_sw)
    painter.setBrush(QBrush(kolory["tuleje"], Qt.SolidPattern))
    painter.drawPath(tuleje)
    painter.setBrush(QBrush(kolory["sworznie"], Qt.SolidPattern))
    painter.drawPath(sworznie)


class AnimationView(QWidget):
    def __init__(self, parent, dane):
        super().__init__(parent)
        self.animacja = Animacja(self, dane)
        self.start_event = threading.Event()
        self.ghost_event = threading.Event()
        self.ghost_event.set()
        threading.Thread(target = self.animacja.startAnimacji, args=(self.start_event, self.ghost_event)).start()

        main_layout = QVBoxLayout()
        animation_controls = QGridLayout()
        bcgrd = QWidget(self)
        bcgrd.setStyleSheet("QPushButton { padding: 4px; min-height: 15px;}")
        bcgrd.setMaximumHeight(80)
        self.start_animation_button = QPushButton("START ANIMACJI", bcgrd)
        self.restet_animacji = QPushButton("POZYCJA POCZĄTKOWA", bcgrd)
        self.slider = QSlider(Qt.Horizontal, bcgrd)
        self.slider.setMaximum(360)
        self.slider.valueChanged.connect(self.setAngle)
        self.animacja.animation_tick.connect(self.updateSlider)
        self.animacja.reset.connect(self.resetAnimacji)
        self.angle_label = QLabel(bcgrd)
        self.start_animation_button.setMaximumSize(160, 20)
        self.start_animation_button.clicked.connect(self.startPrzycisk)
        self.restet_animacji.setMaximumSize(160, 20)
        self.restet_animacji.clicked.connect(self.resetAnimacji)

        animation_controls.addWidget(self.start_animation_button, 1, 0)
        animation_controls.addWidget(self.restet_animacji, 1, 1)
        animation_controls.addWidget(self.slider, 0, 0, 1, 2)
        animation_controls.addWidget(self.angle_label, 0, 3)
        bcgrd.setLayout(animation_controls)
        main_layout.addWidget(self.animacja)
        main_layout.addWidget(bcgrd)
        main_layout.setAlignment(Qt.AlignHCenter)
        animation_controls.setAlignment(Qt.AlignHCenter)
        main_layout.setContentsMargins(80, 20, 80, 20)
        self.setLayout(main_layout)

    def resizeEvent(self, event: QResizeEvent) -> None:
        new_size = min(event.size().width(), 1000), event.size().height()
        self.animacja.setFixedSize(*new_size)
        self.animacja.updatePaintArea(min(new_size) - 75)
        return super().resizeEvent(event)

    def startPrzycisk(self):
        if self.start_animation_button.text() == "START ANIMACJI":
            self.start_animation_button.setText("STOP ANIMACJI")
            self.start_event.set()
        else:
            self.start_animation_button.setText("START ANIMACJI")
            self.start_event.clear()

    def resetAnimacji(self):
        self.start_animation_button.setText("START ANIMACJI")
        self.start_event.clear()
        self.angle_label.setText("0" + "\u00B0")
        self.slider.setValue(0)
        self.animacja.setAngle(0, reset=True)

    def setAngle(self, slider_value):
        # if self.start_event.is_set():
        #     return
        self.angle_label.setText(str(slider_value) + "\u00B0")
        self.animacja.setAngle(slider_value)
    
    def updateSlider(self, value):
        # if not self.start_event.is_set():
        #     return
        self.angle_label.setText(str(-round(value)) + "\u00B0")
        self.slider.blockSignals(True)
        self.slider.setValue(-value)
        self.slider.blockSignals(False)


class Animacja(QLabel):
    animation_tick = Signal(float)
    reset = Signal()

    BRONZE = "#B08D57"
    STEEL = "#CED2D7"
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
        self.skok_kata = 0
        self.paint_area = 700

        self.layout = QGridLayout()
        # self.setAlignment(Qt.AlignLeft)
        # self._size = QSize(self.width(), self.height())
        self.updateAnimationData({})
        self.rysowanko()

    def rysowanko(self):
        # TODO: wygląda na to że invoke dziala nawet jak ta metoda jest wywołana z głównego wątku.
        # jakby co to można podać tu argument mówiący skąd jest wywołana i robić po prostu self.setpixmap
        pxmap = QPixmap(self.size())
        pxmap.fill("#f0f0f0")
        if self.data is None:
            invoke_in_main_thread(lambda: self.setPixmap(pxmap))
            # self.setPixmap(pxmap)
            return
        painter = QPainter(pxmap)
        pen = QPen(Qt.black,1)
        painter.setPen(pen)
        painter.translate(self.paint_area/2, self.paint_area/2)

        liczba_rolek = self.data["z"]+1
        self.skok_kata = 360/liczba_rolek

        kat_dorotacji = -(self.kat_/liczba_rolek)
        if liczba_rolek % 2 == 0:
            kat_dorotacji2 = -((self.kat_+180*liczba_rolek)/liczba_rolek)
        else:
            kat_dorotacji2 = -((self.kat_2+180)/liczba_rolek)

        przesuniecie_x = self.data["e"] * math.cos(self.kat_ * 0.0175) * self.scala
        przesuniecie_y = self.data["e"] * math.sin(self.kat_ * 0.0175) * self.scala

        # Rysowanie pierscienia okalającego :
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala)))/2), -(((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala)))/2, ((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala)),((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala)))
        painter.setBrush(QBrush(self.WHITE, Qt.SolidPattern))
        painter.drawEllipse((-(((self.data["Rg"] * self.scala * 2)))/ 2),-(((self.data["Rg"] * self.scala * 2))) / 2,((self.data["Rg"] * self.scala * 2)),((self.data["Rg"] * self.scala * 2)))

        painter.rotate(kat_dorotacji)
        if self.data_wiktor is not None:
            rysowanie_tuleje(painter, self.scala, self.data_wiktor, {"tuleje": self.BRONZE,"sworznie": self.STEEL})
        
        if self.data["K"] == 2:
            painter.translate(przesuniecie_x, przesuniecie_y)
            painter.setBrush(QBrush(self.PASTEL_BLUE2, Qt.SolidPattern))
            if self.data_wiktor is None:
                painter.drawPath(self.zarys)
            else:
                zarys_otw = wytnij_otwory(self.zarys, self.scala, self.data_wiktor, 0)
                painter.drawPath(zarys_otw)
            painter.translate(-przesuniecie_x, -przesuniecie_y)
        
        painter.rotate(-kat_dorotacji+kat_dorotacji2)
        painter.translate(przesuniecie_x, przesuniecie_y)
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        if self.data_wiktor is None:
            painter.drawPath(self.zarys)
        elif liczba_rolek % 2 != 0:
            # ta dziwna liczba to poczatkawa wartość kat_dorotacji2
            zarys_otw = wytnij_otwory(self.zarys, self.scala, self.data_wiktor, -((180*liczba_rolek+180)/liczba_rolek))
            painter.drawPath(zarys_otw)
        else:
            zarys_otw = wytnij_otwory(self.zarys, self.scala, self.data_wiktor, -180)
            painter.drawPath(zarys_otw)
        painter.translate(-przesuniecie_x, -przesuniecie_y)
        painter.rotate(-kat_dorotacji2)

        #Rysowanie rolek :
        painter.setBrush(QBrush(self.GRAY_LIGHT, Qt.SolidPattern))
        for i in range(liczba_rolek):
            x = self.data["Rg"] * math.cos(i * self.skok_kata * 0.0175) * self.scala
            y = self.data["Rg"] * math.sin(i * self.skok_kata * 0.0175) * self.scala
            painter.drawEllipse(x-(self.data["g"]*self.scala),y-(self.data["g"]*self.scala),self.data["g"]*self.scala*2,self.data["g"]*self.scala*2)

        # Rysowanie punktu mimośrodu
        # pen2 = QPen(Qt.red, 3)
        # painter.setPen(pen2)
        # painter.drawPoint(0, 0)

        # if self.data_wiktor is not None:
        #     pr = self.data_wiktor["R_wt"] * self.scala
        #     painter.drawArc(-pr, -pr, pr*2, pr*2, 0, 16 * 360)

        #Rysowanie punktu "C"
        #xp = self.data[8]*math.cos(kat_dorotacji* 0.0175)
        #yp = self.data[8]*math.sin(kat_dorotacji* 0.0175)
        #painter.drawPoint(xp,yp)

        painter.end()
        invoke_in_main_thread(lambda: self.setPixmap(pxmap))

    def setAngle(self, new_angle, reset=False):
        if reset:
            self.kat_ = 0
        else:
            self.kat_ = new_angle*(self.data["z"]+1)
            # dla ustawiania obrotu kola
            # self.kat_ = self.kat_ // 360 + new_angle
        self.kat_2 = self.kat_ + 180*(self.data["z"]+1)
        self.rysowanko()
        self.animation_tick.emit(-self.kat_/(self.data["z"]+1))

    def startAnimacji(self, event, ghost_event):
        while ghost_event.is_set():
            while event.is_set():
                time.sleep(0.04)
                self.kat_ += self.skok_kata
                self.kat_2 += self.skok_kata
                self.rysowanko()

                if self.data is None:
                    return

                self.animation_tick.emit(-self.kat_/(self.data["z"]+1))
                if self.kat_ >= 360*(self.data["z"]+1):
                    self.kat_ = 0
                    self.kat_2 = 180*(self.data["z"]+1)

    def updatePaintArea(self, paint_area):
        self.paint_area = paint_area
        if self.data is None:
            return

        self.updateAnimationData({})
        self.rysowanko()

    def updateAnimationData(self, data):
        old_z = self.data["z"] if self.data is not None else None
        if data.get("GearTab") == False:
            self.data = None
            self.rysowanko()
            return
        elif data.get("GearTab") is not None:
            self.data = data["GearTab"]
        elif self.data is None:
            return
        
        if data.get("PinOutTab") == False:
            self.data_wiktor = None
        elif data.get("PinOutTab") is not None:
            self.data_wiktor = data["PinOutTab"]
        
        max_size = (self.data["Rg"] * 2) + (self.data["g"] * 4)
        self.scala = self.paint_area / max_size

        self.zarys = tworz_zarys_kola(self.data["z"], self.data["ro"], self.data["lam"], self.data["g"], self.scala)
        if self.data["z"] != old_z:
            self.reset.emit()
            # self.setAngle(0, True)
        self.rysowanko()


class InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, fn): #, *args, **kwargs):
        QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn

class Invoker(QtCore.QObject):
    def event(self, event):
        event.fn()
        return True

_invoker = Invoker()

def invoke_in_main_thread(fn):
    QtCore.QCoreApplication.postEvent(_invoker, InvokeEvent(fn))