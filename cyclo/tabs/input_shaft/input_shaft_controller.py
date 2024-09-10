from ..common.Itab_controller import ITabController
from .input_shaft_tab import InputShaftTab

class InputShaftTabController(ITabController):
    def __init__(self, gear_tab: InputShaftTab):
        self.tab = gear_tab
