from PySide6.QtWidgets import QWidget, QLabel,QFrame,QStackedLayout, QGridLayout, QVBoxLayout, QDoubleSpinBox, QSpinBox, QPushButton
from PySide6.QtGui import QPalette, QColor, QPainter, QPixmap,Qt, QPolygon, QGradient, QPen,QBrush
from PySide6.QtCore import QLine, QPoint, QSize
import math

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class DataEdit(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout1 = QGridLayout()

                    #z    ro    h    g  a1 a2 f1 f2 w1 w2 b  rg g  e  h
        self.dane = [24, 4.8, 0.625, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.refil_data()
        self.spin_z = SpinBox(self.dane[0],8,38,1)
        self.spin_z.lineEdit().setReadOnly(True)
        self.spin_ro = SpinBox(self.dane[1],3,8,0.05)
        self.spin_h = SpinBox(self.dane[2],0.5,0.99,0.01)
        self.spin_g = SpinBox(self.dane[3],5,14,0.02)

        self.spin_z.valueChanged.connect(self.z_changed)
        self.spin_ro.valueChanged.connect(self.z_changed)
        self.spin_h.valueChanged.connect(self.z_changed)
        self.spin_g.valueChanged.connect(self.z_changed)

        layout.addWidget(QLabelD("DANE WEJSCIOWE :"))
        layout.addWidget(QLabelD("Liczba Zębów [z]"))
        layout.addWidget(self.spin_z)
        layout.addWidget(QLabelD("Promień [ρ]"))
        layout.addWidget(self.spin_ro)
        layout.addWidget(QLabelD("Wsp. wysokości zęba [λ]"))
        layout.addWidget(self.spin_h)
        layout.addWidget(QLabelD("Promień rolek [g]"))
        layout.addWidget(self.spin_g)
        layout.addSpacing(50)
        self.Ra1 = QLabelD(str(round(self.dane[4],2)))
        self.Rf1 = QLabelD(str(round(self.dane[5],2)))
        self.Rw1 = QLabelD(str(round(self.dane[6],2)))
        self.Ra2 = QLabelD(str(round(self.dane[7],2)))
        self.Rf2 = QLabelD(str(round(self.dane[8],2)))
        self.Rw2 = QLabelD(str(round(self.dane[9],2)))
        self.Rb = QLabelD(str(round(self.dane[10],2)))
        self.Rg = QLabelD(str(round(self.dane[11],2)))
        self.g = QLabelD(str(round(self.dane[12],2)))
        self.e = QLabelD(str(round(self.dane[13],2)))
        self.h = QLabelD(str(round(self.dane[14],2)))

        layout1.addWidget(QLabelD("DANE : "),0,0,1,2)
        layout1.addWidget(QLabelD("Ra1 : "), 1, 0)
        layout1.addWidget(self.Ra1, 1, 1)
        layout1.addWidget(QLabelD("Rf1 : "), 2, 0)
        layout1.addWidget(self.Rf1, 2, 1)
        layout1.addWidget(QLabelD("Rw1 : "), 3, 0)
        layout1.addWidget(self.Rw1, 3, 1)
        layout1.addWidget(QLabelD("Ra2 : "), 4, 0)
        layout1.addWidget(self.Ra2, 4, 1)
        layout1.addWidget(QLabelD("Rf2 : "), 5, 0)
        layout1.addWidget(self.Rf2, 5, 1)
        layout1.addWidget(QLabelD("Rw2 : "), 6, 0)
        layout1.addWidget(self.Rw2, 6, 1)
        layout1.addWidget(QLabelD("Rb : "), 7, 0)
        layout1.addWidget(self.Rb, 7, 1)
        layout1.addWidget(QLabelD("Rg : "), 8, 0)
        layout1.addWidget(self.Rg, 8, 1)
        layout1.addWidget(QLabelD("g : "), 9, 0)
        layout1.addWidget(self.g, 9, 1)
        layout1.addWidget(QLabelD("e : "), 10, 0)
        layout1.addWidget(self.e, 10, 1)
        layout1.addWidget(QLabelD("h : "), 11, 0)
        layout1.addWidget(self.h, 11, 1)



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
        self.Ra1.setText(str(round(self.dane[4], 2)))
        self.Rf1.setText(str(round(self.dane[5], 2)))
        self.Rw1.setText(str(round(self.dane[6], 2)))
        self.Ra2.setText(str(round(self.dane[7], 2)))
        self.Rf2.setText(str(round(self.dane[8], 2)))
        self.Rw2.setText(str(round(self.dane[9], 2)))
        self.Rb.setText(str(round(self.dane[10], 2)))
        self.Rg.setText(str(round(self.dane[11], 2)))
        self.g.setText(str(round(self.dane[12], 2)))
        self.e.setText(str(round(self.dane[13], 2)))
        self.h.setText(str(round(self.dane[14], 2)))



    def z_changed(self):

        self.dane[0] = self.spin_z.value()
        self.dane[1] = self.spin_ro.value()
        self.dane[2] = self.spin_h.value()
        self.dane[3] = self.spin_g.value()

        self.refil_data()
        self.refili_labels()
        update = Animacja(self.dane)
        print("CP"+str(self.dane[0]))
class SpinBox(QDoubleSpinBox):
    def __init__(self,a,b,c,d):
        super().__init__()

        self.setValue(a)
        self.lineEdit().setReadOnly(False)
        self.setRange(b, c)
        self.setSingleStep(d)

class Tab_Pawel(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        self.layout = QGridLayout()
        self.data = DataEdit()
        self.animacja = Animacja(self.data.dane)
        self.data.spin_z.valueChanged.connect(self.zmiana_danych)
        self.data.spin_ro.valueChanged.connect(self.zmiana_danych)
        self.data.spin_g.valueChanged.connect(self.zmiana_danych)
        self.data.spin_h.valueChanged.connect(self.zmiana_danych)
        self.layout.addWidget(self.data,0,0,4,1)
        self.layout.addWidget(self.animacja, 0, 1,4,5)
        main_layout.addLayout(self.layout)
        self.setLayout(main_layout)

    def zmiana_danych(self):
        self.animacja.rysowanko()
        print("HEH")
        self.layout.addWidget(self.animacja,0,1,4,5)

class QLabelD(QLabel):
    def __init__(self,a):
        super().__init__()

        self.setText(str(a))
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)

class Animacja(QWidget):

    def __init__(self, data):
        super().__init__()

        self.setMinimumSize(640,640)
        self.data=data

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
        print(str(self.data[0]))

        #skalowanie rysunku :
        scala = (self.data[1] * (self.data[0] + 1) * math.cos(0)) - (self.data[2] * self.data[1] * (math.cos((self.data[0] + 1) * 0))) - ((self.data[3] * ((math.cos(0) - (self.data[2] * math.cos((self.data[0] + 1) * 0))) / (math.sqrt(1 - (2 * self.data[2] * math.cos(self.data[0] * 0)) + (self.data[2] * self.data[2]))))))
        scala = (200/scala)

        # rysowanie zarysu :
        for j in range(0,1440):
            i=j/4
            x = (self.data[1] * (self.data[0] + 1) * math.cos(i * 0.0175)) - (self.data[2] * self.data[1] * (math.cos((self.data[0] + 1) * i * 0.0175))) - ((self.data[3] * ((math.cos(i * 0.0175) - (self.data[2] * math.cos((self.data[0] + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * self.data[2] * math.cos(self.data[0] * i * 0.0175)) + (self.data[2] * self.data[2]))))))
            y = (self.data[1] * (self.data[0] + 1) * math.sin(i * 0.0175)) - (self.data[2] * self.data[1] * (math.sin((self.data[0] + 1) * i * 0.0175))) - ((self.data[3] * ((math.sin(i * 0.0175) - (self.data[2] * math.sin((self.data[0] + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * self.data[2] * math.cos(self.data[0] * i * 0.0175)) + (self.data[2] * self.data[2]))))))
            x=x*scala
            y=y*scala
            points.insert(j, QPoint(x+320, y+320))
        painter.drawPolygon(points)

        #Rysowanie rolek :

        painter.setBrush(QBrush(Qt.green))
        liczba_rolek = int(self.data[0])
        skok_kata = 360/liczba_rolek

        for i in range(liczba_rolek):
            x=320+self.data[11]*math.cos(i*skok_kata* 0.0175)*scala
            y = 320 + self.data[11] * math.sin(i * skok_kata * 0.0175) * scala
            painter.drawEllipse(x-(self.data[12]*scala),y-(self.data[12]*scala),self.data[12]*scala*2,self.data[12]*scala*2)

        #Rysowanie Wałka

        painter.setBrush(QBrush(Qt.yellow))
        painter.drawEllipse(320-(10*scala),320-(10*scala),20*scala,20*scala)


        self.setLayout(self.layout)
        self.label.setPixmap(pixmap)
        painter.end()




