from ..view.ResultsTab import ResultsTab

from ....utils.dict_utils import extract_data, update_data_subset

class ResultsTabController:
    def __init__(self, id: int, tab: ResultsTab, mediator):
        self._id = id
        self._tab = tab
        self._mediator = mediator

    def _connect_signals_and_slots(self):
        self._tab.updateStateSignal.connect(self.update_state)

    def init_state(self, component_data):
        """
        Override parent method. Set the initial data for the tab from the parent's data.

        Args:
            component_data (dict): Component data.
        """
        self._component_data = component_data

        outputs_keys = [['nwe'], ['Mwe'], ['L'], ['LA'], ['LB'], ['L1'], ['Lc'], ['e'],
                        ['Fx'], ['Ra'], ['Rb'], ['P'],
                        ['Bearings', 'support_A', 'P'],
                        ['Bearings', 'support_B', 'P'],
                        ['Bearings', 'eccentrics', 'P']
                        ]

        self._outputs = extract_data(self._component_data, outputs_keys)

        self._tab.initUI(self._outputs)
        self._connect_signals_and_slots()
    
    def update_state(self):
        """
        Update the tab with component data.
        """
        def update_output(recipient, source, attribute):
            new_value = source[attribute][0]
            if new_value is not None:
                recipient[attribute][0].setValue(new_value)

        update_data_subset(self._component_data, self._outputs, update_output)
