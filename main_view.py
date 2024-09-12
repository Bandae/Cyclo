from PySide2.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QSlider
from PySide2.QtCore import Qt
from PySide2.QtGui import QResizeEvent

from animation import Animacja

class AnimationView(QWidget):
    """Main widget for managing the animation view and its controls."""
    def __init__(self, parent, dane):
        super().__init__(parent)
        self.dane = dane

        self._initUI()

        # Start and stop signals are managed internally, no ghost_event
        self.is_animation_running = False

    def _initUI(self):
        """Initializes the UI elements and layout."""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignHCenter)
        main_layout.setContentsMargins(80, 20, 80, 20)
        self.setLayout(main_layout)

        # Set animation
        self.animacja = Animacja(self, self.dane)
        self.animacja.animation_tick.connect(self.updateSlider)
        self.animacja.reset.connect(self.resetAnimacji)

        bcgrd = QWidget(self)
        bcgrd.setStyleSheet("QPushButton { padding: 4px; min-height: 15px;}")
        bcgrd.setMaximumHeight(80)

        animation_controls = QGridLayout()
        animation_controls.setAlignment(Qt.AlignHCenter)
        bcgrd.setLayout(animation_controls)

        # Set button for starting/stopping the animation
        self.start_animation_button = QPushButton("START ANIMACJI", bcgrd)
        self.start_animation_button.setMaximumSize(160, 20)
        self.start_animation_button.clicked.connect(self.startPrzycisk)

        # Set button for resetting animation
        self.restet_animacji = QPushButton("POZYCJA POCZĄTKOWA", bcgrd)
        self.restet_animacji.setMaximumSize(160, 20)
        self.restet_animacji.clicked.connect(self.resetAnimacji)

        # Set slider for viewing the cycloidal wheel at a given angle
        self.slider = QSlider(Qt.Horizontal, bcgrd)
        self.slider.setMaximum(360)
        self.slider.valueChanged.connect(self.setAngle)

        # Set label to display the current angle
        self.angle_label = QLabel(bcgrd)

        # Add controls to the layout
        animation_controls.addWidget(self.start_animation_button, 1, 0)
        animation_controls.addWidget(self.restet_animacji, 1, 1)
        animation_controls.addWidget(self.slider, 0, 0, 1, 2)
        animation_controls.addWidget(self.angle_label, 0, 3)

        main_layout.addWidget(self.animacja)
        main_layout.addWidget(bcgrd)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handles window resize events and adjusts the animation area."""
        new_size = min(event.size().width(), 1000), event.size().height()
        self.animacja.setFixedSize(*new_size)
        self.animacja.updatePaintArea(min(new_size) - 75)
        return super().resizeEvent(event)

    def startPrzycisk(self):
        """Starts or stops the animation based on the current button state."""
        if not self.is_animation_running:
            self.start_animation_button.setText("STOP ANIMACJI")
            self.animacja.startAnimacji()  # Start the animation (thread)
            self.is_animation_running = True
        else:
            self.start_animation_button.setText("START ANIMACJI")
            self.animacja.stopAnimacji()  # Stop the animation (thread)
            self.is_animation_running = False

    def resetAnimacji(self):
        """Resets the animation to the initial position."""
        self.start_animation_button.setText("START ANIMACJI")
        self.animacja.stopAnimacji()  # Ensure the animation stops before resetting
        self.is_animation_running = False
        self.angle_label.setText("0" + "\u00B0")
        self.slider.setValue(0)
        self.animacja.setAngle(0, reset=True)

    def setAngle(self, slider_value):
        """Sets the current angle of the cycloidal wheel based on the slider value."""
        self.angle_label.setText(str(slider_value) + "\u00B0")
        self.animacja.setAngle(slider_value)

    def updateSlider(self, value):
        """Updates the slider position based on the current angle of the animation."""
        self.angle_label.setText(str(-round(value)) + "\u00B0")
        self.slider.blockSignals(True)
        self.slider.setValue(-value)
        self.slider.blockSignals(False)
    
    def closeEvent(self, event):
        """Handle app closure to ensure thread is stopped."""
        if self.animacja.worker is not None:
            self.animacja.stopAnimacji()
        event.accept()  # Accept the close event
