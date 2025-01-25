from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGridLayout, QFrame
from common_widgets import QLabelD, IntSpinBox


class BaseDataWidget(QFrame):
    dataChanged = Signal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        layout = QGridLayout()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setFixedSize(200, 170)

        self.input_data = {
            "M_wyj": 500,
            "n_wej": 1000,
            "i": 24,
        }
        self.input_widgets = {
            "M_wyj": IntSpinBox(self.input_data["M_wyj"], 50, 2000, 10),
            "n_wej": IntSpinBox(self.input_data["n_wej"], 50, 2000, 10),
            "i": IntSpinBox(self.input_data["i"], 6, 80, 1),
        }

        top_label = QLabelD("Dane wejściowe", style=False)
        top_label.setMaximumHeight(20)
        layout.addWidget(top_label, 0, 0, 1, 5)
        layout.addWidget(QLabelD("Moment wyjściowy [Nm]", style=False), 1, 0, 1, 4)
        layout.addWidget(self.input_widgets["M_wyj"], 1, 4)
        layout.addWidget(QLabelD("Prędkość obr. wejściowa [obr/min]", style=False), 2, 0, 1, 4)
        layout.addWidget(self.input_widgets["n_wej"], 2, 4)
        layout.addWidget(QLabelD("Przełożenie", style=False), 3, 0, 1, 4)
        layout.addWidget(self.input_widgets["i"], 3, 4)

        for widget in self.input_widgets.values():
            widget.valueChanged.connect(self.inputsModified)
            
        self.setLayout(layout)
    
    def inputsModified(self):
        for key, widget in self.input_widgets.items():
            self.input_data[key] = widget.value()
        
        self.dataChanged.emit({"base": self.input_data})
    
    def saveData(self):
        return self.input_data

    def loadData(self, new_data):
        if new_data is None:
            return
        for key in self.input_widgets:
            self.input_widgets[key].setValue(new_data[key])
    
    def reportData(self):
        def indent_point(point_text):
            return f"{{\\pard\\sa50\\fi-300\\li600\\bullet\\b\\tab {point_text} \\par}}"
        
        text = "{\\pard\\sa100\\b Dane wejściowe: \\par}"
        text += indent_point(f"Obciążenie: M{{\sub wyj}} = {self.input_data['M_wyj']} [Nm]")
        text += indent_point(f"Prędkość obrotowa wałka wejściowego: n{{\sub wej}} = {self.input_data['n_wej']} [obr/min]")
        text += indent_point(f"Przełożenie: i = {self.input_data['i']}")
        text += "\\line"
        return text
