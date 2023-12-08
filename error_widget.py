from PySide2.QtWidgets import QWidget, QVBoxLayout
from common_widgets import QLabelD


class ErrorWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.errors = {
            "R_wk duze": QLabelD("Dla obecnych danych, otwory nie zmieszczą się w kole cykloidalnym. Zmniejsz R<sub>wk</sub> lub wróć do edycji zarysu."),
            "R_wk male": QLabelD("Dla obecnych danych, otwory w kole cykloidalnym przecinają się. Zwiększ R<sub>wk</sub>, lub zmniejsz średnicę tuleji."),
        }
        for widget in self.errors.values():
            widget.setMinimumHeight(80)
            layout.addWidget(widget)
            # widget.setStyleSheet("QLabel { color: red; padding: 10px;}")
            widget.setStyleSheet("QLabel { color: red; }")
            # Dlaczego sie psuje jak  dam widget.hide() ??
        self.setLayout(layout)
        layout.setSpacing(10)
    
    def updateErrors(self, errors):
        for key in errors:
            if errors[key]:
                self.errors[key].show()
            else:
                self.errors[key].hide()

    def resetErrors(self):
        for widget in self.errors.values():
            widget.hide()

    def errorsExist(self):
        return any([error.isVisible() for error in self.errors.values()])
