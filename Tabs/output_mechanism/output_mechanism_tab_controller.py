
from .output_mechanism_tab import OutputMechanismTab
from ..common.Itab_controller import ITabController

class OutputMechanismTabController(ITabController):
    def __init__(self, output_mechanism_tab: OutputMechanismTab):
        self.tab = output_mechanism_tab

        self.connect_signals_and_slots()

    def connect_signals_and_slots(self):
        self.tab.use_this_check.stateChanged.connect(self.tab.useThisChanged)