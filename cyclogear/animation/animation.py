import math
import time
from PySide2.QtCore import QThread, QPoint, Qt, QObject, Signal 
from PySide2.QtGui import QPainter, QPixmap, QPolygon, QPen, QBrush, QPainterPath
from PySide2.QtWidgets import QLabel

# TODO: skok kąta zmienia się przy liczbie zębów. Więc dla niektoych liczb zębów, self._angle może sie zdarzyć nie taki jak trzeba jak sie zmienia poza animacją.
# reset animacji to naprawia od razu, ale nie jej start. jest to kwestia kumulacji błędów, bo jak lece od 24 do 10 to sie zepsuje, ale jak zresetuje na 11 i zejde do 10 to już nie.
# narazie ustawiam reset jeśli było zmienione przełożenie/liczba zębów. Inny pomysł mam, żeby zmienić self._angle do najbliższego podzielnego przez skok kąta, to powinno działać

class Animation(QLabel):
    """
    This class is responsible for handling the drawing and updating of the animated cycloidal wheel.
    
    It manages the visual representation of the wheel, including the current angle of rotation. The class
    works together with the `AnimationWorker` to update the wheel's angle in a background thread while 
    ensuring that the graphical updates and UI interactions (like the slider and angle label) are 
    performed in the main thread.

    The class also provides methods for starting and stopping the animation, updating the angle based 
    on user input or automated updates, and redrawing the current frame of the animation.
    """
    animationTick = Signal(float)  # Signal to update the slider and angle label
    reset = Signal()

    BACKGROUND_COLOR = "#f0f0f0"
    BRONZE = "#B08D57"
    STEEL = "#CED2D7"
    WHITE = "#FFFFFF"
    GRAY_LIGHT = "#B4B4B4"
    GRAY = "#323434"
    GRAY_DARK = "#92929"
    PASTEL_BLUE = '#ADD8E6'
    PASTEL_BLUE2 = '#BDE4E6'

    def __init__(self, parent):
        """
        Args:
            parent (QWidget): Reference to the parent widget
            data (dict): Contains the parameters and configuration for the cycloidal wheel.
        """
        super().__init__(parent)

        self._data = None
        self._dataWiktor = None
        self._angle = 0
        # TODO: temporary solution while working on gear tab starting out with empty fields
        self._angle2 = 180 * (24 + 1)
        # self._angle2 = 180 * (self._data["z"] + 1)
        self._angleStep = 0
        self._paintArea = 700

        self._worker = None
        self._animationThread = None

        self.setMinimumSize(750, 750)
        # self.updateData({})
        # self._draw()

    def _draw(self):
        """
        Draws the current frame of the animation.
        """
        # Create a pixmap with the size of the widget and fill it with the background color
        pixmap = QPixmap(self.size())
        pixmap.fill(self.BACKGROUND_COLOR)
        
        if self._data is None:
            return

        painter = QPainter(pixmap)
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        # Translate the origin to the center of the paint area
        painter.translate(self._paintArea / 2, self._paintArea / 2)
        
        # Calculate the number of rollers and angle step:
        rollers_count = self._data["z"] + 1  # Number of rollers (or pins/teeth)
        self._angleStep = 360 / rollers_count  # Step of the angle in degrees

        # Calculate rotation angle for the rollers
        rotation_angle = -(self._angle / rollers_count)
        
        # Secondary rotation angle calculation, based on whether rollers count is even or odd
        if rollers_count % 2 == 0:
            secondary_rotation_angle = -((self._angle + 180 * rollers_count) / rollers_count)
        else:
            secondary_rotation_angle = -((self._angle2 + 180) / rollers_count)

        # Calculate translation for eccentric movement
        translation_x = self._data["e"] * math.cos(self._angle * 0.01745329) * self.scale
        translation_y = self._data["e"] * math.sin(self._angle * 0.01745329) * self.scale

        # Draw the outer ring of the wheel
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        painter.drawEllipse(
            -(((self._data["Rg"] * self.scale * 2) + (self._data["g"] * 4 * self.scale)) / 2),
            -(((self._data["Rg"] * self.scale * 2) + (self._data["g"] * 4 * self.scale)) / 2),
            ((self._data["Rg"] * self.scale * 2) + (self._data["g"] * 4 * self.scale)),
            ((self._data["Rg"] * self.scale * 2) + (self._data["g"] * 4 * self.scale))
        )
        
        # Draw the inner circle of the outer ring
        painter.setBrush(QBrush(self.WHITE, Qt.SolidPattern))
        painter.drawEllipse(
            -(((self._data["Rg"] * self.scale * 2)) / 2),
            -(((self._data["Rg"] * self.scale * 2)) / 2),
            ((self._data["Rg"] * self.scale * 2)),
            ((self._data["Rg"] * self.scale * 2))
        )

        # Rotate and draw components relative to the wheel's rotation
        painter.rotate(rotation_angle)
        if self._dataWiktor is not None:
            # Draw bushings and pins
            drawBushingsAndPins(painter, self.scale, self._dataWiktor, {'bushings': self.BRONZE, 'pins': self.STEEL})

        # Handle additional components based on configuration
        if self._data["K"] == 2:
            painter.translate(translation_x, translation_y)
            painter.setBrush(QBrush(self.PASTEL_BLUE2, Qt.SolidPattern))
            
            # Draw the cycloidal shape or cut holes if necessary
            if self._dataWiktor is None:
                painter.drawPath(self._outline)
            else:
                cutout_shape = cutHoles(self._outline, self.scale, self._dataWiktor, 0)
                painter.drawPath(cutout_shape)
            painter.translate(-translation_x, -translation_y)

        # Rotate back and translate to the original position
        painter.rotate(-rotation_angle + secondary_rotation_angle)
        painter.translate(translation_x, translation_y)
        
        # Set brush color and draw the inner shape
        painter.setBrush(QBrush(self.PASTEL_BLUE, Qt.SolidPattern))
        if self._dataWiktor is None:
            painter.drawPath(self._outline)
        elif rollers_count % 2 != 0:
            cutout_shape = cutHoles(self._outline, self.scale, self._dataWiktor, -((180 * rollers_count + 180) / rollers_count))
            painter.drawPath(cutout_shape)
        else:
            cutout_shape = cutHoles(self._outline, self.scale, self._dataWiktor, -180)
            painter.drawPath(cutout_shape)

        painter.translate(-translation_x, -translation_y)
        painter.rotate(-secondary_rotation_angle)

        # Draw the rollers around the outer ring
        painter.setBrush(QBrush(self.GRAY_LIGHT, Qt.SolidPattern))
        for i in range(rollers_count):
            x = self._data["Rg"] * math.cos(i * self._angleStep * 0.01745329) * self.scale
            y = self._data["Rg"] * math.sin(i * self._angleStep * 0.01745329) * self.scale
            painter.drawEllipse(x - (self._data["g"] * self.scale), y - (self._data["g"] * self.scale), self._data["g"] * self.scale * 2, self._data["g"] * self.scale * 2)
        
        # Optional: Draw eccentric point (currently commented out)
        # pen2 = QPen(Qt.red, 3)
        # painter.setPen(pen2)
        # painter.drawPoint(0, 0)

        # Optional: Draw additional arc (currently commented out)
        # if self._dataWiktor is not None:
        #     pr = self._dataWiktor["R_wt"] * self.scale
        #     painter.drawArc(-pr, -pr, pr * 2, pr * 2, 0, 16 * 360)

        # Optional: Draw point "C" (currently commented out)
        # xp = self._data[8] * math.cos(rotation_angle * 0.01745329)
        # yp = self._data[8] * math.sin(rotation_angle * 0.01745329)
        # painter.drawPoint(xp, yp)

        # End painting and apply the pixmap to the widget
        painter.end()

        # Ensure the widget is updated with the new pixmap
        self.setPixmap(pixmap)
        self.update()  # Trigger the widget to repaint with the new pixmap
        
    def _onRedrawAnimation(self):
        """
        Triggered by redrawAnimation signal emited by AnimationWorker. It emits
        signal to update slider position and angle label and
        calls function updating cycloidal gear animation.
        """
        self.animationTick.emit(-self._angle / (self._data["z"] + 1))
        self._draw()

    def start(self):
        """
        Starts the animation by moving the worker to a QThread.
        """
        if self._animationThread is None:
            # Set the animation thread
            self._animationThread = QThread()
           
            # Set the animation worker
            self._worker = AnimationWorker(self)

            self._worker.moveToThread(self._animationThread)                    # Move the worker to a thread
            self._worker.redrawAnimation.connect(self._onRedrawAnimation)       # Connect the worker's redraw request signal to the drawing function in the main thread
            self._animationThread.started.connect(self._worker.run)

            # Start the thread
            self._animationThread.start()

    def stop(self):
        """
        Stops the animation and cleans up the thread.
        """
        if self._worker is not None:
            self._worker.stop()
            self._animationThread.quit()
            self._animationThread.wait()
            self._animationThread = None
            self._worker = None

    def setAngle(self, newAngle, reset=False):
        """
        Updates the current angle of animation based on slider value.
        """
        if reset:
            self._angle = 0
        else:
            self._angle = newAngle * (self._data["z"] + 1)
        self._angle2 = self._angle + 180 * (self._data["z"] + 1)
        self._draw()

    def updatePaintArea(self, paintArea):
        """
        Updates the paint area dimensions when the window is resized.
        """
        self._paintArea = paintArea
        if self._data is None:
            return

        self.updateData({})
        self._draw()

    def updateData(self, data):
        """
        Updates the animation data and recalculates components if necessary.
        """
        # TODO: to jest wciąż potrzebne, aby poprawnie był rysowany mechanizm wyj.
        oldTeethCount = self._data["z"] if self._data is not None else None
        if data.get("GearTab") is False:
            self._data = None
            self._draw()
            return
        elif data.get("GearTab") is not None:
            self._data = data["GearTab"]
        elif self._data is None:
            return

        if data.get("PinOutTab") is False:
            self._dataWiktor = None
        elif data.get("PinOutTab") is not None:
            self._dataWiktor = data["PinOutTab"]

        max_size = (self._data["Rg"] * 2) + (self._data["g"] * 4)
        self.scale = self._paintArea / max_size

        self._outline = drawGearOutline(self._data["z"], self._data["ro"], self._data["lam"], self._data["g"], self.scale)
        if self._data["z"] != oldTeethCount:
            self.reset.emit()
        self._draw()

def drawGearOutline(teethCount, baseRadius, heightFactor, displacementFactor, scale):
    """
    Creates the outline of a cycloidal gear wheel based on the given parameters.
    Args:
        teethCount: The number of teeth on the gear.
        baseRadius: The base radius of the gear.
        heightFactor: Factor related to the height of the gear's profile.
        displacementFactor: Factor related to the displacement of the gear's profile.
        scale: Scaling factor for the dimensions.
    Returns:
        A QPainterPath object representing the gear's outline.
    """
    outline = QPainterPath()
    points = QPolygon()

    # Loop to calculate the points of the gear outline
    for pointIndex in range(720):
        angle = pointIndex / 2  # Angle step in degrees, divided by 2 to get 360 degrees
        # Calculate x-coordinate based on cycloidal formula
        x = (baseRadius * (teethCount + 1) * math.cos(angle * 0.01745329)) \
            - (heightFactor * baseRadius * math.cos((teethCount + 1) * angle * 0.01745329)) \
            - (displacementFactor * ((math.cos(angle * 0.01745329) 
            - (heightFactor * math.cos((teethCount + 1) * angle * 0.01745329))) / (math.sqrt(1 
            - (2 * heightFactor * math.cos(teethCount * angle * 0.01745329)) + (heightFactor ** 2)))))
        
        # Calculate y-coordinate based on cycloidal formula
        y = (baseRadius * (teethCount + 1) * math.sin(angle * 0.01745329)) \
            - (heightFactor * baseRadius * math.sin((teethCount + 1) * angle * 0.01745329)) \
            - (displacementFactor * ((math.sin(angle * 0.01745329) 
            - (heightFactor * math.sin((teethCount + 1) * angle * 0.01745329))) / (math.sqrt(1 
            - (2 * heightFactor * math.cos(teethCount * angle * 0.01745329)) + (heightFactor ** 2)))))
        
        # Insert the calculated point into the polygon
        points.insert(pointIndex, QPoint(x * scale, y * scale))

    # Add the calculated points as a polygon to the outline path
    outline.addPolygon(points)
    
    return outline

def cutHoles(outlinePath, scale, bushingData, initialRotationDegrees):
    """
    Cuts circular holes in the wheel's outline.
    
    Args:
        outlinePath: The QPainterPath object representing the wheel's outline.
        scale: The scaling factor for the coordinates.
        bushingData: Dictionary containing the bushing configuration.
        initialRotationDegrees: The initial rotation in degrees.
    Returns:
        The modified QPainterPath with holes cut out.
    """
    bushingsCount = bushingData["n"]  # Number of bushings
    bushingRadius = bushingData["R_wt"]  # Radius for the bushing placement circle
    holeDiameter = bushingData["d_otw"] * scale  # Diameter of each hole (scaled)

    holesPath = QPainterPath()

    # Calculate the position of each bushing hole and add it to the path
    for bushingIndex in range(bushingsCount):
        # Angular position of each bushing in radians
        bushingAngle = (2 * math.pi * bushingIndex) / bushingsCount
        
        # Convert the initial rotation from degrees to radians (0.01745329 = pi/180)
        rotationRadians = initialRotationDegrees * 0.01745329

        # Calculate the x and y coordinates for the center of the hole
        holeCenterX = (bushingRadius * math.cos(bushingAngle - rotationRadians)) * scale - holeDiameter / 2
        holeCenterY = (bushingRadius * math.sin(bushingAngle - rotationRadians)) * scale - holeDiameter / 2

        # Add an ellipse (representing the hole) to the path
        holesPath.addEllipse(holeCenterX, holeCenterY, holeDiameter, holeDiameter)

    # Return the outline path with the holes subtracted
    return outlinePath.subtracted(holesPath)

def drawBushingsAndPins(painter, scale, bushingData, colors):
    """
    Draws the bushings and pins on the cycloidal wheel.
    
    Args:
        painter: The QPainter object used to draw.
        scale: The scaling factor for the dimensions.
        bushingData: Dictionary containing data related to the bushings.
        colors: Dictionary of colors for drawing the bushings and pins.
    """
    bushingsCount = bushingData["n"]  # Number of bushings
    bushingRadius = bushingData["R_wt"]  # Radius for the bushing placement circle
    pinDiameter = bushingData["d_sw"] * scale  # Diameter of the pins (scaled)
    bushingDiameter = bushingData["d_tul"] * scale  # Diameter of the bushings (scaled)

    bushingPath = QPainterPath()
    pinPath = QPainterPath()

    # Loop through and calculate the position of each bushing and pin
    for bushingIndex in range(bushingsCount):
        # Angular position of each bushing/pin in radians
        bushingAngle = (2 * math.pi * bushingIndex) / bushingsCount

        # Calculate the x and y coordinates for the bushing/pin center
        bushingCenterX = (bushingRadius * math.cos(bushingAngle)) * scale
        bushingCenterY = (bushingRadius * math.sin(bushingAngle)) * scale

        # Add an ellipse for the bushing
        bushingPath.addEllipse(bushingCenterX - bushingDiameter / 2, bushingCenterY - bushingDiameter / 2, bushingDiameter, bushingDiameter)
        
        # Add an ellipse for the pin
        pinPath.addEllipse(bushingCenterX - pinDiameter / 2, bushingCenterY - pinDiameter / 2, pinDiameter, pinDiameter)

    # Set the brush to the bushing color and draw the bushings
    painter.setBrush(QBrush(colors["bushings"], Qt.SolidPattern))
    painter.drawPath(bushingPath)

    # Set the brush to the pin color and draw the pins
    painter.setBrush(QBrush(colors["pins"], Qt.SolidPattern))
    painter.drawPath(pinPath)

class AnimationWorker(QObject):
    """
    This class is responsible for managing the animation loop in a background thread.
    
    It continuously updates the angles of the cycloidal wheel and triggers a redraw in the main 
    thread via a signal. The goal is to separate the time-consuming animation logic from the 
    main thread to avoid blocking the GUI's responsiveness. The worker updates the wheel's 
    angles and emits a request to redraw the animation in the main thread.
    """
    redrawAnimation = Signal()  # Signal to request drawing in the main thread

    def __init__(self, animation: Animation):
        """
        Args:
            animation (Animation): Reference to the `Animacja` class which handles the animation logic and rendering.
        """
        super().__init__()
        self.animation = animation
        self._is_running = False

    def run(self):
        """
        Main animation loop. Continuously updates the angle and requests a redraw until stopped.
        """
        self._is_running = True

        try:
            while self._is_running:
                time.sleep(0.04)  # Control animation speed
                self.animation._angle += self.animation._angleStep
                self.animation._angle2 += self.animation._angleStep
                
                # Emit a signal to request redrawing in the main thread
                self.redrawAnimation.emit()

                # TODO: nie jestem pewien czy rzeczywiście jest potrzeba tego resetu po różnych zmianach w animacji...
                # Angle is reset to 0 every full rotation of the gear to eliminate inaccuracies adding up over time
                if self.animation._angle >= 360 * (self.animation._data["z"] + 1):
                    self.animation._angle = 0
                    self.animation._angle2 = 180 * (self.animation._data["z"] + 1)
        except Exception as e:
            print(f"Thread error: {e}")

    def stop(self):
        """
        Stops the animation loop
        """
        self._is_running = False
