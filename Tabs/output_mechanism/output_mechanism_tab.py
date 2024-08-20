from PySide2.QtWidgets import QLabel, QHBoxLayout, QStackedLayout, QVBoxLayout, QCheckBox
from tabs.common.widgets.abstract_tab import AbstractTab
from PySide2.QtCore import Signal

class OutputMechanismTab(AbstractTab):
    this_enabled = Signal(bool)
    def __init__(self, parent):
        super().__init__(parent)

        self._init_ui()
    
    def _init_ui(self):
        # Set main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Set checkbox layout
        self.checkbox_layout = QHBoxLayout()
        self.main_layout.addLayout(self.checkbox_layout)

        # Set navigation buttons layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        # Set subtabs layout
        self.stacklayout = QStackedLayout()
        self.main_layout.addLayout(self.stacklayout)

        self._init_checkbox()
        self._init_subtabs()

    def _init_checkbox(self):
        self.use_this_check = QCheckBox(text="Używaj tego mechanizmu wyjściowego")
        
        self.checkbox_layout.addWidget(self.use_this_check)    

    def _init_subtabs(self):
        label = QLabel("Mechanizm wyjściowy z rolkami - w trakcie rozwoju")
        self.stacklayout.addWidget(label)
    
    def useThisChanged(self, state):
        if state:
            # TODO: wlaczyc wszystkie mozliwosci wprowadzania danych
            # self.data.setEnabled(False)
            self.this_enabled.emit(True)
        else:
            self.this_enabled.emit(False)
            # TODO: wylaczyc wszystkie mozliwosci wprowadzania danych
            # self.data.setEnabled(True)
    
    def useOtherChanged(self, state):
        self.use_this_check.setEnabled(not state)
