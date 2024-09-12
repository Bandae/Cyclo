import math
import time
from PySide2.QtCore import QThread, QPoint, Qt, QObject, Signal 
from PySide2.QtGui import QPainter, QPixmap, QPolygon, QPen, QBrush, QPainterPath
from PySide2.QtWidgets import QLabel

# TODO: skok kąta zmienia się przy liczbie zębów. Więc dla niektoych liczb zębów, self.kat_ może sie zdarzyć nie taki jak trzeba jak sie zmienia poza animacją.
# reset animacji to naprawia od razu, ale nie jej start. jest to kwestia kumulacji błędów, bo jak lece od 24 do 10 to sie zepsuje, ale jak zresetuje na 11 i zejde do 10 to już nie.
# narazie ustawiam reset jeśli było zmienione przełożenie/liczba zębów. Inny pomysł mam, żeby zmienić self.kat_ do najbliższego podzielnego przez skok kąta, to powinno działać

class Animacja(QLabel):
    """
    This class is responsible for handling the drawing and updating of the animated cycloidal wheel.
    
    It manages the visual representation of the wheel, including the current angle of rotation. The class
    works together with the `AnimationWorker` to update the wheel's angle in a background thread while 
    ensuring that the graphical updates and UI interactions (like the slider and angle label) are 
    performed in the main thread.

    The class also provides methods for starting and stopping the animation, updating the angle based 
    on user input or automated updates, and redrawing the current frame of the animation.
    """
    animation_tick = Signal(float)  # Signal to update the angle
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
        """
        Args:
            parent (QWidget): Reference to the parent widget
            data (dict): Contains the parameters and configuration for the cycloidal wheel.
        """
        super().__init__(parent)

        self.setMinimumSize(750, 750)
        self.data = data
        self.data_wiktor = None
        self.kat_ = 0
        self.kat_2 = 180 * (self.data["z"] + 1)
        self.skok_kata = 0
        self.paint_area = 700

        self.worker = None
        self.animation_thread = None

        self.updateAnimationData({})
        self.rysowanko()
    
    def startAnimacji(self):
        """
        Starts the animation by moving the worker to a QThread.
        """
        if self.animation_thread is None:
            # Set the animation thread
            self.animation_thread = QThread()
           
            # Set the animation worker
            self.worker = AnimationWorker(self)

            self.worker.moveToThread(self.animation_thread)         # Move the worker to a thread
            self.worker.request_redraw.connect(self.onRedraw)       # Connect the worker's redraw request signal to the drawing function in the main thread
            self.animation_thread.started.connect(self.worker.run)

            # Start the thread
            self.animation_thread.start()

    def stopAnimacji(self):
        """
        Stops the animation and cleans up the thread.
        """
        if self.worker is not None:
            self.worker.stop()
            self.animation_thread.quit()
            self.animation_thread.wait()
            self.animation_thread = None
            self.worker = None
    
    def onRedraw(self):
        """
        Triggered by request_redraw signal emited by AnimationWorker. It emits
        signal with angle value to update slider position and angle label and
        calls function updating cycloidal gear animation.
        """
        self.animation_tick.emit(-self.kat_ / (self.data["z"] + 1))
        self.rysowanko()

    def rysowanko(self):
        """Draws the current frame of the animation."""
        pxmap = QPixmap(self.size())
        pxmap.fill("#f0f0f0")
        if self.data is None:
            return

        painter = QPainter(pxmap)
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        painter.translate(self.paint_area / 2, self.paint_area / 2)

        liczba_rolek = self.data["z"] + 1
        self.skok_kata = 360 / liczba_rolek

        # Calculate rotation and translation
        kat_dorotacji = -(self.kat_ / liczba_rolek)
        if liczba_rolek % 2 == 0:
            kat_dorotacji2 = -((self.kat_ + 180 * liczba_rolek) / liczba_rolek)
        else:
            kat_dorotacji2 = -((self.kat_2 + 180) / liczba_rolek)

        przesuniecie_x = self.data["e"] * math.cos(self.kat_ * 0.0175) * self.scala
        przesuniecie_y = self.data["e"] * math.sin(self.kat_ * 0.0175) * self.scala

        # Draw the outer ring of the wheel
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        painter.drawEllipse(
            -(((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala)) / 2),
            -(((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala)) / 2),
            ((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala)),
            ((self.data["Rg"] * self.scala * 2) + (self.data["g"] * 4 * self.scala))
        )
        painter.setBrush(QBrush(self.WHITE, Qt.SolidPattern))
        painter.drawEllipse(
            -(((self.data["Rg"] * self.scala * 2)) / 2),
            -(((self.data["Rg"] * self.scala * 2)) / 2),
            ((self.data["Rg"] * self.scala * 2)),
            ((self.data["Rg"] * self.scala * 2))
        )

        # Rotate and draw components
        painter.rotate(kat_dorotacji)
        if self.data_wiktor is not None:
            rysowanie_tuleje(painter, self.scala, self.data_wiktor, {"tuleje": self.BRONZE, "sworznie": self.STEEL})

        if self.data["K"] == 2:
            painter.translate(przesuniecie_x, przesuniecie_y)
            painter.setBrush(QBrush(self.PASTEL_BLUE2, Qt.SolidPattern))
            if self.data_wiktor is None:
                painter.drawPath(self.zarys)
            else:
                zarys_otw = wytnij_otwory(self.zarys, self.scala, self.data_wiktor, 0)
                painter.drawPath(zarys_otw)
            painter.translate(-przesuniecie_x, -przesuniecie_y)

        painter.rotate(-kat_dorotacji + kat_dorotacji2)
        painter.translate(przesuniecie_x, przesuniecie_y)
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        if self.data_wiktor is None:
            painter.drawPath(self.zarys)
        elif liczba_rolek % 2 != 0:
            zarys_otw = wytnij_otwory(self.zarys, self.scala, self.data_wiktor, -((180 * liczba_rolek + 180) / liczba_rolek))
            painter.drawPath(zarys_otw)
        else:
            zarys_otw = wytnij_otwory(self.zarys, self.scala, self.data_wiktor, -180)
            painter.drawPath(zarys_otw)
        painter.translate(-przesuniecie_x, -przesuniecie_y)
        painter.rotate(-kat_dorotacji2)

        # Draw rollers
        painter.setBrush(QBrush(self.GRAY_LIGHT, Qt.SolidPattern))
        for i in range(liczba_rolek):
            x = self.data["Rg"] * math.cos(i * self.skok_kata * 0.0175) * self.scala
            y = self.data["Rg"] * math.sin(i * self.skok_kata * 0.0175) * self.scala
            painter.drawEllipse(x - (self.data["g"] * self.scala), y - (self.data["g"] * self.scala), self.data["g"] * self.scala * 2, self.data["g"] * self.scala * 2)
        
        # Draw eccentric point
        # pen2 = QPen(Qt.red, 3)
        # painter.setPen(pen2)
        # painter.drawPoint(0, 0)

        # if self.data_wiktor is not None:
        #     pr = self.data_wiktor["R_wt"] * self.scala
        #     painter.drawArc(-pr, -pr, pr*2, pr*2, 0, 16 * 360)

        #Draw point "C"
        #xp = self.data[8]*math.cos(kat_dorotacji* 0.0175)
        #yp = self.data[8]*math.sin(kat_dorotacji* 0.0175)
        #painter.drawPoint(xp,yp)

        painter.end()

        # Ensure the widget is updated with the new pixmap
        self.setPixmap(pxmap)
        self.update()  # Make sure to update the widget to reflect the changes

    def setAngle(self, new_angle, reset=False):
        """Updates the current angle of animation based on slider value."""
        if reset:
            self.kat_ = 0
        else:
            self.kat_ = new_angle * (self.data["z"] + 1)
        self.kat_2 = self.kat_ + 180 * (self.data["z"] + 1)
        self.rysowanko()

    def updatePaintArea(self, paint_area):
        """Updates the paint area dimensions when the window is resized."""
        self.paint_area = paint_area
        if self.data is None:
            return

        self.updateAnimationData({})
        self.rysowanko()

    def updateAnimationData(self, data):
        """Updates the animation data and recalculates components if necessary."""
        old_z = self.data["z"] if self.data is not None else None
        if data.get("GearTab") is False:
            self.data = None
            self.rysowanko()
            return
        elif data.get("GearTab") is not None:
            self.data = data["GearTab"]
        elif self.data is None:
            return

        if data.get("PinOutTab") is False:
            self.data_wiktor = None
        elif data.get("PinOutTab") is not None:
            self.data_wiktor = data["PinOutTab"]

        max_size = (self.data["Rg"] * 2) + (self.data["g"] * 4)
        self.scala = self.paint_area / max_size

        self.zarys = tworz_zarys_kola(self.data["z"], self.data["ro"], self.data["lam"], self.data["g"], self.scala)
        if self.data["z"] != old_z:
            self.reset.emit()
        self.rysowanko()

def tworz_zarys_kola(z, ro, h, g, scala):
    """Creates the outline of a cycloidal wheel based on the given parameters."""
    zarys = QPainterPath()
    points = QPolygon()
    for j in range(0, 720):
        i = j / 2
        x = (ro * (z + 1) * math.cos(i * 0.0175)) - (h * ro * (math.cos((z + 1) * i * 0.0175))) - ((g * ((math.cos(i * 0.0175) - (h * math.cos((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
        y = (ro * (z + 1) * math.sin(i * 0.0175)) - (h * ro * (math.sin((z + 1) * i * 0.0175))) - ((g * ((math.sin(i * 0.0175) - (h * math.sin((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
        points.insert(j, QPoint(x * scala, y * scala))
    zarys.addPolygon(points)
    return zarys

def wytnij_otwory(zarys, scala, dane_wiktor, obrot_poczatkowy):
    """Cuts circular holes in the wheel's outline."""
    liczba_tuleji = dane_wiktor["n"]
    R_wt = dane_wiktor["R_wt"]
    d_otw = dane_wiktor["d_otw"] * scala

    otwory = QPainterPath()

    for i in range(liczba_tuleji):
        fi_kj = (2 * math.pi * i) / liczba_tuleji
        x_okj = (R_wt * math.cos(fi_kj - obrot_poczatkowy * 0.0175)) * scala - d_otw / 2
        y_okj = (R_wt * math.sin(fi_kj - obrot_poczatkowy * 0.0175)) * scala - d_otw / 2
        otwory.addEllipse(x_okj, y_okj, d_otw, d_otw)

    return zarys.subtracted(otwory)

def rysowanie_tuleje(painter, scala, dane_wiktor, kolory):
    """Draws the bushings and pins on the cycloidal wheel."""
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


class AnimationWorker(QObject):
    """
    This class is responsible for managing the animation loop in a background thread.
    
    It continuously updates the angles of the cycloidal wheel and triggers a redraw in the main 
    thread via a signal. The goal is to separate the time-consuming animation logic from the 
    main thread to avoid blocking the GUI's responsiveness. The worker updates the wheel's 
    angles and emits a request to redraw the animation in the main thread.
    """
    request_redraw = Signal()  # Signal to request drawing in the main thread

    def __init__(self, animacja: Animacja):
        """
        Args:
            animacja (Animacja): Reference to the `Animacja` class which handles the animation logic and rendering.
        """
        super().__init__()
        self.animacja = animacja
        self._is_running = False

    def run(self):
        """
        Main animation loop. Continuously updates the angle and requests a redraw until stopped.
        """
        self._is_running = True

        try:
            while self._is_running:
                time.sleep(0.04)  # Control animation speed
                self.animacja.kat_ += self.animacja.skok_kata
                self.animacja.kat_2 += self.animacja.skok_kata
                
                # Emit a signal to request redrawing in the main thread
                self.request_redraw.emit()

                # Check if the angle exceeds 360 and reset
                if self.animacja.kat_ >= 360 * (self.animacja.data["z"] + 1):
                    self.animacja.kat_ = 0
                    self.animacja.kat_2 = 180 * (self.animacja.data["z"] + 1)
        except Exception as e:
            print(f"Thread error: {e}")

    def stop(self):
        """
        Stops the animation loop
        """
        self._is_running = False