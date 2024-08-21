from functools import partial

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedLayout, QCheckBox

from tabs.common.widgets.abstract_tab import AbstractTab

from ..subtabs.entry_data.entry_data_tab import EntryDataTab
from common.common_widgets import ResponsiveContainer
from ...common.widgets.tolerance_widgets import ToleranceEdit
from ...common.widgets.charts import ResultsTab
#TODO: mam przesunięte do tyłu w poziomie punkty wykresów. Pawel też.
# moze jakos usuwac dane z wykresow jak sa bledy?
# po trzy razy wysylam dane w niektorych sytuacjach, np jak sie zaznaczy zeby uzywac tego. Może to jest pętla.
#TODO: moze zrobic w animacji painter.save() i .restore() zamiast obrotów -self.kat_dorotacji
#TODO: ukrywanie label e2 teraz jak jest QSCrollArea nie dziala, bo to sie dzieje na zewnatrz, pokazanie wszystkich widzetow

class PinOutTab(AbstractTab):
    thisEnabled = Signal(bool)
    def __init__(self) -> None:
        super().__init__()

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

        self.use_this_check.stateChanged.connect(self.useThisChanged)

    def _init_subtabs(self):
        # Set DataEdit subtab
        self.data = EntryDataTab(self)
        scrollable_tab = ResponsiveContainer(self, self.data, self.data.setupSmallLayout, self.data.setupLayout, 620, 1200)

        # Set Results subtab
        self.wykresy = ResultsTab(self, "numer sworznia", {
            "sily": {"repr_name": "Siły", "chart_title": "Siły na sworzniach", "y_axis_title": "Siła [N]"},
            "naciski": {"repr_name": "Naciski", "chart_title": "Naciski powierzchniowe na sworzniach", "y_axis_title": "Wartość Nacisku [MPa]"},
            "straty": {"repr_name": "Straty", "chart_title": "Straty mocy na sworzniach", "y_axis_title": "Straty mocy [W]"},
            "luzy": {"repr_name": "Luzy", "chart_title": "Luzy na sworzniach", "y_axis_title": "Luz [mm]"},
        })

        # Set Tolerances subtab
        self.tol_edit = ToleranceEdit(self, (
            ("T_o", "T<sub>o</sub>", "Tolerancja wykonania promieni otworów w kole cykloidalnym"),
            ("T_t", "T<sub>t</sub>", "Tolerancja wykonania promieni tuleji"),
            ("T_s", "T<sub>s</sub>", "Tolerancja wykonania promieni sworzni"),
            ("T_Rk", "T<sub>Rk</sub>", "Tolerancja wykonania promienia rozmieszczenia otworów w kole cykloidalnym"),
            ("T_Rt", "T<sub>Rt</sub>", "Tolerancja wykonania promienia rozmieszczenia tulei w elemencie wyjściowym"),
            ("T_fi_k", "T<sub>\u03c6k</sub>", "Tolerancja wykonania kątowego rozmieszczenia otworów w kole cykloidalnym"),
            ("T_fi_t", "T<sub>\u03c6t</sub>", "Tolerancja wykonania kątowego rozmieszczenia tulei w elemencie wyjściowym"),
            ("T_e", "T<sub>e</sub>", "Tolerancja wykonania mimośrodu"),
        ))

        # Add subtabs and their navigation buttons to the tab 
        tab_titles = ["Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        stacked_widgets = [scrollable_tab, self.wykresy, self.tol_edit]

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            button = QPushButton(title)
            self.button_layout.addWidget(button)
            self.stacklayout.addWidget(widget)
            button.pressed.connect(partial(self.stacklayout.setCurrentIndex, index))

        # Add help button
        self.help_pdf_button = QPushButton("Pomoc")
        self.button_layout.addWidget(self.help_pdf_button)

        # Initially, disable data and tolerances tabs
        self.data.setEnabled(False)
        self.tol_edit.setEnabled(False)
    
    def useThisChanged(self, state: bool) -> None:
        self.data.setEnabled(state)
        self.tol_edit.setEnabled(state)
        if state:
            self.thisEnabled.emit(True)
            self.data.module_enabled = True
            self.data.recalculate()
        else:
            self.thisEnabled.emit(False)
            self.data.module_enabled = False
            self.data.animDataUpdated.emit({"PinOutTab": False})

    def useOtherChanged(self, state: bool) -> None:
        self.use_this_check.setEnabled(not state)
