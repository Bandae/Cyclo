from PySide6.QtWidgets import QWidget, QLabel,QFrame, QGridLayout, QVBoxLayout, QDoubleSpinBox, QSpinBox, QPushButton
from PySide6.QtGui import QPalette, QColor

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
        self.dane = [20, 4.8, 0.625, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.refil_data()
        self.spin_z = SpinBox(self.dane[0],8,38,1)
        self.spin_z.lineEdit().setReadOnly(True)
        self.spin_ro = SpinBox(self.dane[1],3,8,0.05)
        self.spin_h = SpinBox(self.dane[2],0.5,1,0.01)
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
        self.Ra1 = QLabelD(str(self.dane[4]))
        self.Rf1 = QLabelD(str(self.dane[5]))
        self.Rw1 = QLabelD(str(self.dane[6]))
        self.Ra2 = QLabelD(str(self.dane[7]))
        self.Rf2 = QLabelD(str(self.dane[8]))
        self.Rw2 = QLabelD(str(self.dane[9]))
        self.Rb = QLabelD(str(self.dane[10]))
        self.Rg = QLabelD(str(self.dane[11]))
        self.g = QLabelD(str(self.dane[12]))
        self.e = QLabelD(str(self.dane[13]))
        self.h = QLabelD(str(self.dane[14]))

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

        self.dane[0]=self.spin_z.value()
        self.dane[1] = self.spin_ro.value()
        self.dane[2] = self.spin_h.value()
        self.dane[3] = self.spin_g.value()

        self.refil_data()
        self.refili_labels()

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
        layout = QGridLayout()
        self.data = DataEdit()
        layout.addWidget(self.data,0,0,4,1)
        layout.addWidget(Color('gray'), 0, 1,3,5)
        layout.addWidget(Color('gray'), 3, 1,1,5)
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

class QLabelD(QLabel):
    def __init__(self,a):
        super().__init__()

        self.setText(str(a))
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)