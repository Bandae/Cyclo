from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QSlider
from PySide2.QtCore import Qt
from PySide2.QtGui import QResizeEvent

from animation import Animation

class AnimationControls(QWidget):
    """
    A custom widget that provides controls for starting/stopping, resetting, and adjusting 
    the animation of the cycloidal wheel.
    """
    def __init__(self, parent):
        """
        Initializes the AnimationControls widget, which includes buttons for controlling
        the animation and a slider for adjusting the angle of the cycloidal wheel.
        """
        super().__init__(parent)

        # Set style
        self.setStyleSheet("QPushButton { padding: 4px; min-height: 15px;}")
        self.setMaximumHeight(80)

        # Set layout
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(layout)

        # Set button for starting/stopping the animation
        self.toggleAnimationButton = QPushButton(self)
        self.toggleAnimationButton.setCheckable(True)
        self.toggleAnimationButton.setMaximumSize(160, 20)
        self.toggleAnimationButton.toggled.connect(self._updateAnimationButtonLabel)
        self.toggleAnimationButtonLabelOff = 'START ANIMACJI'
        self.toggleAnimationButtonLabelOn = 'STOP ANIMACJI'
        self.toggleAnimationButton.setText(self.toggleAnimationButtonLabelOff)

        # Set button for resetting animation
        self.resetAnimationButton = QPushButton("RESET ANIMACJI", self)
        self.resetAnimationButton.setMaximumSize(160, 20)

        # Set slider for viewing the cycloidal wheel at a given angle
        self.animationSlider = QSlider(Qt.Horizontal, self)
        self.animationSlider.setMaximum(360)
        self.animationSlider.valueChanged.connect(self._setAngleLabel)
        
        # Set label to display the current angle
        self.angleLabel = QLabel(self)

        # Add controls to the layout
        layout.addWidget(self.toggleAnimationButton, 1, 0)
        layout.addWidget(self.resetAnimationButton, 1, 1)
        layout.addWidget(self.animationSlider, 0, 0, 1, 2)
        layout.addWidget(self.angleLabel, 0, 3)
    
    def _updateAnimationButtonLabel(self, checked):
        """
        Updates the label of the toggle button to show 'START ANIMACJI' or 'STOP ANIMACJI'
        depending on whether the animation is running or stopped.
        
        Args:
            checked (bool): A boolean indicating whether the button is checked (animation running).
        """
        if checked:
            self.toggleAnimationButton.setText(self.toggleAnimationButtonLabelOn)
        else:
            self.toggleAnimationButton.setText(self.toggleAnimationButtonLabelOff)
    
    def _setAngleLabel(self, sliderValue):
        """
        Updates the angle label to reflect the current position of the slider in degrees.

        Args:
            sliderValue (float): The current value of the slider.
        """
        self.angleLabel.setText(str(round(sliderValue)) + "\u00B0")
    
    def resetAnimationControls(self):
        """
        Resets the controls to their default state: the start/stop button is set to 'START ANIMACJI',
        and the slider is reset to the zero angle position.
        """
        if self.toggleAnimationButton.isChecked():
            self.toggleAnimationButton.toggle()
        self.animationSlider.setValue(0)

    def setSliderPosition(self, angleValue):
        """
        Sets the slider position to a given angle value. Signals from the slider are blocked 
        while the position is updated to prevent unnecessary events being triggered.
        
        Args:
            angleValue (float): The angle value to set the slider to.
        """
        self.animationSlider.blockSignals(True)
        self.animationSlider.setValue(-angleValue)
        self._setAngleLabel(-angleValue)
        self.animationSlider.blockSignals(False)

class AnimationView(QWidget):
    """
    Main widget for managing the animation view and its controls.
    """
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data

        self._initUI()

    def _initUI(self):   
        """
        Initializes the UI elements and layout.
        """
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignHCenter)
        mainLayout.setContentsMargins(80, 20, 80, 20)
        self.setLayout(mainLayout)

        # Set animation
        self.animation = Animation(self, self.data)

        # Set animation controls
        self.animationControls = AnimationControls(self)

        # Connect signals and slots
        self.animation.animationTick.connect(self.animationControls.setSliderPosition)
        self.animation.reset.connect(self._resetAnimation)
        self.animationControls.toggleAnimationButton.toggled.connect(self._toggleAnimation)
        self.animationControls.resetAnimationButton.clicked.connect(self._resetAnimation)
        self.animationControls.animationSlider.valueChanged.connect(self.animation.setAngle)

        mainLayout.addWidget(self.animation)
        mainLayout.addWidget(self.animationControls)

    def _toggleAnimation(self, runAnimation):
        """
        Starts or stops the animation based on the current state of toggleAnimationButton.

        Args:
            runAnimation (bool): Bollean value indicating if the toggleAnimationButton is checked 
                                 (1 - animation not running, 0 - animation running)                 
        """
        if runAnimation:
            self.animation.start()  # Start the animation (thread)
        else:
            self.animation.stop()  # Stop the animation (thread)

    def _resetAnimation(self):
        """
        Resets the animation and its contrtols to the initial position.
        """
        self.animationControls.resetAnimationControls()
        self.animation.setAngle(0, reset=True)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handles window resize events and adjusts the animation area.
        Args:
            event (QResizeEvent): Resize event of this widget.
        """
        new_size = min(event.size().width(), 1000), event.size().height()
        self.animation.setFixedSize(*new_size)
        self.animation.updatePaintArea(min(new_size) - 75)
        return super().resizeEvent(event)
    
    def closeEvent(self, event):
        """
        Handle app closure to ensure thread is stopped.
        Args:
            event (QCloseEvent): Close event of this widget 
        """
        self.animation.stop()
        event.accept()  # Accept the close event
