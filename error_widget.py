from typing import Dict, Optional
from PySide2.QtWidgets import QWidget, QVBoxLayout
from common_widgets import QLabelD


class ErrorWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.errors = {
            "PinOutTab": {
                "R_wt duze": QLabelD("Dla obecnych danych, otwory nie zmieszczą się w kole cykloidalnym. Zmniejsz R<sub>wk</sub> lub wróć do edycji zarysu."),
                "R_wt male": QLabelD("Dla obecnych danych, otwory w kole cykloidalnym przecinają się. Zwiększ R<sub>wk</sub>, lub zmniejsz średnicę tuleji."),
                "naciski przekroczone": QLabelD("Przekroczono dopuszczalne naciski w mechanizmie wyjściowym. Zmień parę materiałów, lub zmniejsz obciążenie."),
            },
            "GearTab": {
                "podcinanie zebow": QLabelD("Zęby koła podstawowego są podcinane. Zmień parametry zazębienia. Zwłaszcza zwiększ ρ lub λ."),
                "sasiedztwo rolek": QLabelD("Warunek sąsiedztwa rolek nie jest spełniony. Zmień parametry zazębienia. Zwłaszcza zmniejsz g, lub zwiększ ρ lub λ."),
                "Rg male": QLabelD("Zbyt mały promień rozmieszczenia rolek. Zmień parametry zazębienia."),
                # "g duze": QLabelD("Zbyt duży promień rolek. Zmniejsz g."),
                # "e duze": QLabelD("Zbyt duży mimośród. Zmniejsz ρ lub λ."),
                "naciski przekroczone": QLabelD("Przekroczono dopuszczalne naciski między kołem a rolkami. Zmień parę materiałów, lub zmniejsz obciążenie."),
            }
        }
        for module_name in self.errors:
            for label in self.errors[module_name].values():
                label.setMinimumHeight(80)
                label.setMaximumHeight(130)
                layout.addWidget(label)
                # label.setStyleSheet("QLabel { color: red; padding: 10px;}")
                label.setStyleSheet("QLabel { color: red; }")
                # Dlaczego sie psuje jak  dam label.hide() ??
        layout.addStretch()
        layout.setSpacing(10)
        self.setLayout(layout)
    
    def updateErrors(self, errors: Optional[Dict[str, bool]]=None, module: Optional[str]=None) -> None:
        target_module = module if self.errors.get(module) else None
        if not target_module:
            return
        if not errors:
            self.resetErrors(module)
            return

        for error_name, label in self.errors[target_module].items():
            if error_name in errors:
                label.show()
            else:
                label.hide()

    def resetErrors(self, module: str="all") -> None:
        for module_name in self.errors:
            if module == "all" or module == module_name:
                for label in self.errors[module_name].values():
                    label.hide()

    def errorsExist(self) -> bool:
        return any([error.isVisible() for module_name in self.errors for error in self.errors[module_name].values()])
