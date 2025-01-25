from PySide2.QtWidgets import QDialog, QVBoxLayout, QApplication, QHBoxLayout, QStyle, QSpacerItem, QSizePolicy
from PySide2.QtGui import QFontMetrics
from PySide2.QtCore import QSize, Qt

from .Label import Label
from .PushButton import PushButton

class MessageDialog(QDialog):
    '''
    Custom QMessageBox designed to enhance window resizing flexibility and accommodate long titles. 
    This custom dialog is particularly useful because it prevents the truncation of lengthy titles, 
    ensuring they are fully displayed.
    ''' 
    def __init__(self, parent, title, message, iconType):
        super().__init__(parent)

        self.title = title
        self.message = message
        self.iconType = iconType

        # Set window flags to keep only the title bar
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)

        self.setWindowTitle(title)

        self.layout = QVBoxLayout(self)

        self._initMessage()
        self._initButtons()

        titleFont = QApplication.font()
        fontMetrics = QFontMetrics(titleFont)
        titleWidth = fontMetrics.horizontalAdvance(self.title) + 150  # Add some padding
        messageWidth = 200 + 32 + 20  # Text width + icon width + padding
        width = max(titleWidth, messageWidth)
        self.setMinimumWidth(width)

    def _initMessage(self):
        # Message layout
        messageLayout = QHBoxLayout()
        self.layout.addLayout(messageLayout)

        # Message type icon
        self.iconLabel = Label()
        self.iconLabel.setFixedWidth(50)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = self.style().standardIcon(self.iconType)
        self.iconLabel.setPixmap(icon.pixmap(QSize(32, 32)))
        messageLayout.addWidget(self.iconLabel)

        # Message label 
        self.messageLabel = Label(self.message)
        self.messageLabel.setWordWrap(True)
        messageLayout.addWidget(self.messageLabel)

    def _initButtons(self):
        # Buttons layout
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(20)
        self.layout.addLayout(buttonLayout)

        if self.iconType == QStyle.StandardPixmap.SP_MessageBoxQuestion:
            buttonLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

            # Yes Button
            self.yesButton = PushButton("Tak")
            self.yesButton.setFixedWidth(80)
            self.yesButton.clicked.connect(self.accept)
            buttonLayout.addWidget(self.yesButton)

            # No button
            self.noButton = PushButton("Nie")
            self.noButton.setFixedWidth(80)
            self.noButton.clicked.connect(self.reject)
            buttonLayout.addWidget(self.noButton)

            buttonLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        else:
            # OK button
            self.okButton = PushButton("OK")
            self.okButton.clicked.connect(self.accept)
            self.okButton.setFixedWidth(80)
            buttonLayout.addWidget(self.okButton)

    @classmethod
    def critical(cls, parent, title, message):
        dialog = cls(parent, title, message, QStyle.StandardPixmap.SP_MessageBoxCritical)
        dialog.exec_()

    @classmethod
    def information(cls, parent, title, message):
        dialog = cls(parent, title, message, QStyle.StandardPixmap.SP_MessageBoxInformation)
        dialog.exec_()

    @classmethod
    def question(cls, parent, title, message):
        dialog = cls(parent, title, message, QStyle.StandardPixmap.SP_MessageBoxQuestion)
        return dialog.exec_()

    @classmethod
    def warning(cls, parent, title, message):
        dialog = cls(parent, title, message, QStyle.StandardPixmap.SP_MessageBoxWarning)
        dialog.exec_()
