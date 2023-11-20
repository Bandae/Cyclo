from PySide2.QtWidgets import QLabel, QGridLayout, QStackedLayout, QVBoxLayout, QCheckBox
from abstract_tab import AbstractTab
from PySide2.QtCore import Signal


class Tab_Milosz(AbstractTab):
    enable_other = Signal(bool)
    def __init__(self, parent):
        super().__init__(parent)
        main_layout = QVBoxLayout()
        button_layout = QGridLayout()
        stack_layout = QStackedLayout()

        label = QLabel("Mech wyj z rolkami")
        stack_layout.addWidget(label)

        self.use_this_check = QCheckBox(text="Używaj tego mechanizmu wyjściowego")
        self.use_this_check.stateChanged.connect(self.use_this_changed)
        button_layout.addWidget(self.use_this_check)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(stack_layout)
        self.setLayout(main_layout)
    
    def use_this_changed(self, state):
        self.use_this_check.setEnabled(not state)
        if state:
            # TODO: wlaczyc wszystkie mozliwosci wprowadzania danych
            # self.data.setEnabled(False)
            self.enable_other.emit(False)
        else:
            self.use_this_check.setChecked(False)
            # TODO: wylaczyc wszystkie mozliwosci wprowadzania danych
            # self.data.setEnabled(True)
