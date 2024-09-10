from functools import partial

from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedLayout

from tabs.common.widgets.abstract_tab import AbstractTab

from ..subtabs.entry_data.entry_data_tab import EntryDataTab
from common.common_widgets import ResponsiveContainer
from ...common.widgets.tolerance_widgets import ToleranceEdit
from ...common.widgets.charts import ResultsTab
#TODO: nie podoba mi się obliczanie p_max, jako po prostu największego nacisku z wszystkich. U wiktora jest p_max wiekszy niz na sworzniu czasem, bo sworzen zmienia p jak sie obraca.

class GearTab(AbstractTab):
    def __init__(self) -> None:
        super().__init__()

        self._init_ui()

    def _init_ui(self):
        # Set main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Set navigation buttons layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        # Set subtabs layout
        self.stacklayout = QStackedLayout()
        self.main_layout.addLayout(self.stacklayout)

        # Initialize subtabs
        self._init_subtabs()

    def _init_subtabs(self):
        # Set EntryData subtab
        self.data = EntryDataTab(self)
        scrollable_tab = ResponsiveContainer(self, self.data, self.data.setupSmallLayout, self.data.setupLayout, 480, 1300)

        # Set Results subtab
        self.wykresy = ResultsTab(self, "Numer Rolki [n]", {
            "sily": {"repr_name": "Siły", "chart_title": "Wykres Sił w rolkach", "y_axis_title": "Wartość Siły [N]"},
            "naciski": {"repr_name": "Naprężenia", "chart_title": "Wykres Naprężeń w rolkach", "y_axis_title": "Wartość Nacisku [MPa]"},
            "straty": {"repr_name": "Straty Mocy", "chart_title": "Wykres Strat mocy w rolkach", "y_axis_title": "Wartość Straty [W]"},
            "luzy": {"repr_name": "Luz Międzyzębny", "chart_title": "Wykres luzów międzyzębnych w rolkach", "y_axis_title": "Wartość Luzu [mm]"},
        })

        # Set Tolerances subtab
        self.tolerance_edit = ToleranceEdit(self, (
            ("T_ze", "T<sub>ze</sub>", "Tolerancja wykonanania zarysu koła obiegowego"),
            ("T_Rg", "T<sub>Rg</sub>", "Tolerancja wykonania rolki"),
            ("T_fi_Ri", "T<sub>\u03c6Ri</sub>", "Tolerancja wykonania promienia rozmieszczenia rolek w obudowie"),
            ("T_Rr", "T<sub>Rr</sub>", "Tolerancja kątowego rozmieszczenia rolek w obudowie"),
            ("T_e", "T<sub>e</sub>", "Tolerancja wykonania mimośrodu"),
        ))

        # Add subtabs and their navigation buttons to the tab 
        self.tab_titles = ["Wprowadzanie Danych", "Wykresy", "Tolerancje"]
        self.tab_widgets = [scrollable_tab, self.wykresy, self.tolerance_edit]

        for index, (title, widget) in enumerate(zip(self.tab_titles, self.tab_widgets)):
            button = QPushButton(title)
            self.button_layout.addWidget(button)
            self.stacklayout.addWidget(widget)
            button.pressed.connect(partial(self.stacklayout.setCurrentIndex, index))

        # Add help button
        self.help_pdf_button = QPushButton("Pomoc")
        self.button_layout.addWidget(self.help_pdf_button)
