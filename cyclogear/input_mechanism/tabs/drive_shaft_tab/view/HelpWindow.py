from PySide2.QtWidgets import QDialog, QLabel, QVBoxLayout
from PySide2.QtGui import QPixmap

from config import RESOURCES_PATH, dependencies_path

class HelpWindow(QDialog):
    """
    Custom window for displaying help instructions/ images
    """
    def __init__(self, parent):
        super().__init__(parent)

        # Set title
        self.setWindowTitle("Kształtowanie wału czynnego")

        # Set size
        self.setFixedSize(450, 300)

        # Set layout
        self.setLayout(QVBoxLayout())

        # Set image
        label = QLabel(self)
        pixmap = QPixmap(dependencies_path(f'{RESOURCES_PATH}//images//input_mechanism_preview.png'))
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        
        self.layout().addWidget(label)

    def show(self):
        """
        Override default behaviour - if this window is already shown, 
        triggering show event (clicking on button that opens this window)
        results in hiding it.
        """
        if self.isHidden():
            super().show()
        else:
            self.hide()
