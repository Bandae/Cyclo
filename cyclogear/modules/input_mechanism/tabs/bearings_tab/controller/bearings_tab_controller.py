from functools import partial

from ..view.BearingsTab import BearingsTab
from ..model.bearings_tab_calculator import BearingsTabCalculator

from ....mediator import Mediator

from ....utils.dict_utils import extract_data, fetch_data_subset, update_data_subset

class BearingsTabController:
    def __init__(self, id: int, tab: BearingsTab, calculator: BearingsTabCalculator, mediator: Mediator):
        self._id = id
        self._tab = tab
        self._calculator = calculator
        self._mediator = mediator
    
    def _on_bearing_data_provided(self, section_name, all_data_provided, data_changed):
        """
        View/clear required bearing load capacity and enable/disable button for bearing selection.

        Args:
            section_name (str): Specifies the bearing location.
            all_data_provided (bool): Specifies whether all data regarding the bearing was provided
            data_changed (bool): Specifies whether the data regarding the bearing was changed 
        """
        if all_data_provided and data_changed:
            data = self._calculator.calculate_bearing_load_capacity(section_name, self.get_data())
            self._inputs['Bearings'][section_name]['C'][0].setValue(data)
        elif not all_data_provided:
            self._inputs['Bearings'][section_name]['C'][0].clear()

        self._tab.enable_select_bearing_button(section_name, all_data_provided, data_changed)

    def _connect_signals_and_slots(self):
        """
        Connect signals and slots for interactivity in the tab.
        """
        self._tab.sectionInputsProvided.connect(self._on_bearing_data_provided)
        self._tab.allInputsProvided.connect(self._update_component_data)
        self._tab.updateStateSignal.connect(self.update_state)

        for bearing_section_id, item in self._items['Bearings'].items():
            item['data'].dataChangedSignal.connect(partial(self._mediator.update_bearing, bearing_section_id))
            item['data'].clicked.connect(partial(self._mediator.select_bearing, bearing_section_id, self.get_data()))
            item['bearing_type'].clicked.connect(partial(self._mediator.select_bearing_type, bearing_section_id))

    def _update_component_data(self):
        self._mediator.update_component_data(self._id, self.get_data())

    def on_bearing_type_selected(self, section_name, item_data):
        self._tab.update_selected_bearing_type(section_name, item_data)
    
    def on_bearing_selected(self, section_name, item_data):
        self._tab.update_selected_bearing(section_name, item_data)
    
    def get_data(self):
        """
        Retrieve data from the tab.

        Returns:
            self._tab_data (dict): The entered user data.
        """
        def get_input(recipient, source, attribute):
           recipient[attribute][0] = source[attribute][0].value()
        
        def get_item(recipient, source, attribute):
            recipient[attribute] = source[attribute].data()

        fetch_data_subset(self._tab_data, self._inputs, get_input)
        fetch_data_subset(self._tab_data, self._items, get_item)

        return self._tab_data
    
    def init_state(self, component_data):
        """
        Override parent method. Set the initial data for the tab from the component's data.

        Args:
            component_data (dict): Component data.
        """
        self._component_data = component_data

        inputs_keys = [['Bearings', 'support_A', 'Lh'], ['Bearings', 'support_A', 'fd'], ['Bearings', 'support_A', 'ft'], ['Bearings', 'support_A', 'C'],
                       ['Bearings', 'support_B', 'Lh'], ['Bearings', 'support_B', 'fd'], ['Bearings', 'support_B', 'ft'], ['Bearings', 'support_B', 'C'],
                       ['Bearings', 'eccentrics', 'Lh'], ['Bearings', 'eccentrics', 'fd'], ['Bearings', 'eccentrics', 'ft'], ['Bearings', 'eccentrics', 'C']
                       ]
                    
        outputs_keys = [['Bearings', 'support_A', 'dip'],
                        ['Bearings', 'support_B', 'dip'],
                        ['Bearings', 'eccentrics', 'dip']
                        ]
        
        items = [['Bearings', 'support_A', 'data'], ['Bearings', 'support_A', 'bearing_type'],
                 ['Bearings', 'support_B', 'data'], ['Bearings', 'support_B', 'bearing_type'],
                 ['Bearings', 'eccentrics', 'data'], ['Bearings', 'eccentrics', 'bearing_type'],
                 ]
        
        self._tab_data = extract_data(self._component_data, inputs_keys+items)
        self._inputs = extract_data(self._component_data, inputs_keys)
        self._outputs = extract_data(self._component_data, outputs_keys)
        self._items = extract_data(self._component_data, items)
        self._calculator.init_data(self._component_data, self._inputs, self._outputs)

        self._tab.initUI(self._items, self._inputs, self._outputs)
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
    
    def set_state(self, data):
        """
        Set tab's state.

        Args:
            data (dict): Data to set the state of the tab with.
        """
        self._tab.trackState(False)

        def update_input(recipient, source, attribute):
            new_value = source[attribute][0]
            if new_value is not None:
                recipient[attribute][0].setValue(new_value)
        
        update_data_subset(data, self._inputs, update_input)

        for name, item in self._items['Bearings'].items():
            item['data'].setData(data['Bearings'][name]['data'])

        self.update_state()
        self._tab.trackState(True)
