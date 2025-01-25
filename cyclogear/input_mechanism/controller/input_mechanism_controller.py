from ..mediator import Mediator

from ..model.input_mechanism_calculator import InputMechanismCalculator
from ..view.InputMechanism import InputMechanism
from ..tabs.drive_shaft_tab.view.DriveShaftTab import DriveShaftTab
from ..tabs.drive_shaft_tab.model.drive_shaft_tab_calculator import DriveShaftTabCalculator
from ..tabs.drive_shaft_tab.controller.drive_shaft_tab_controller import DriveShaftTabController

from ..tabs.bearings_tab.view.BearingsTab import BearingsTab
from ..tabs.bearings_tab.model.bearings_tab_calculator import BearingsTabCalculator
from ..tabs.bearings_tab.controller.bearings_tab_controller import BearingsTabController

from ..tabs.power_loss_tab.view.PowerLossTab import PowerLossTab
from ..tabs.power_loss_tab.model.power_loss_calculator import PowerLossTabCalculator
from ..tabs.power_loss_tab.controller.power_loss_controller import PowerLossTabController

from ..tabs.results_tab.view.ResultsTab import ResultsTab
from ..tabs.results_tab.controller.results_tab_controller import ResultsTabController

from shaft_designer.view.ShaftDesigner import ShaftDesigner
from shaft_designer.controller.shaft_designer_controller import ShaftDesignerController

from db_handler.controller.db_controller import DbController
from db_handler.model.db_handler import DbHandler
from db_handler.view.DbItemsWindow import DbItemsWindow

class InputMechanismController:
    """
    Controller for the InputMechanism in the application.

    This class handles the interactions between the model (data) and the view (InputMechanism),
    including initializing the view with data, connecting signals and slots, and handling
    user interactions.
    """
    def __init__(self, model: InputMechanismCalculator, view: InputMechanism):
        """
        Initialize the InputMechanismController.W

        :param data: The data for the application.
        :param view: The InputMechanism (QWidget) instance of the input shaft coomponent's GUI.
        """
        self._input_mechanism = view
        self._calculator = model

        self._startup()
        self._connect_signals_and_slots()

    def _startup(self):
        """Initialize the input shaft widget with necessary data, set up tabs and initialize the shaft designer"""
        self.db_window = DbItemsWindow(self._input_mechanism)
        self.db_controller = DbController(self.db_window)
        self._mediator = Mediator()
        self._calculator.set_initial_data()
        self._initTabs()
        self._init_shaft_designer()

    def _initTabs(self):
        tab_id = 1

        tab1 = DriveShaftTab(self._input_mechanism)
        tab1_calculator = DriveShaftTabCalculator()
        tab1_controller = DriveShaftTabController(tab_id, tab1, tab1_calculator, self._mediator)

        tab_id +=1
        tab2 = BearingsTab(self._input_mechanism)
        tab2_calculator = BearingsTabCalculator()
        tab2_controller = BearingsTabController(tab_id, tab2, tab2_calculator, self._mediator)

        tab_id +=1
        tab3 = PowerLossTab(self._input_mechanism)
        tab3_calculator = PowerLossTabCalculator()
        tab3_controller = PowerLossTabController(tab_id, tab3, tab3_calculator, self._mediator)

        tab_id +=1
        tab4 = ResultsTab(self._input_mechanism)
        tab4_controller = ResultsTabController(tab_id, tab4, self._mediator)

        self.tabs = [tab1, tab2, tab3, tab4]
        self.tab_controllers = [tab1_controller, tab2_controller, tab3_controller, tab4_controller]
        tab_titles = ['Wał Czynny', 'Łożyska', 'Straty Mocy', 'Wyniki']

        for tab_controller in self.tab_controllers:
            data = self._calculator.get_data()
            tab_controller.init_state(data)

        self._input_mechanism.initTabs(self.tabs, tab_titles)

    def _init_shaft_designer(self):
        # Set an instance of shaft designer
        window_title = 'Wał Czynny'
        self._shaft_designer = ShaftDesigner(window_title)

        # Set an instance of shaft designer controller
        self._shaft_designer_controller = ShaftDesignerController(self._shaft_designer, self._mediator)

    def _connect_signals_and_slots(self):
        """
        Connect signals and slots for interactivity in the application.

        This method sets up connections between UI elements and their corresponding
        actions or handlers.
        """
        self._input_mechanism.previewButton.clicked.connect(self._open_shaft_designer_window)
        self._mediator.shaftDesigningFinished.connect(self._on_shaft_designing_finished)

        self._mediator.selectMaterial.connect(self._on_select_materials)
        self._mediator.selectBearingType.connect(self._on_select_bearing_type)
        self._mediator.selectBearing.connect(self._on_select_bearing)
        self._mediator.selectRollingElement.connect(self._on_select_rolling_element)

        self._mediator.updateComponentData.connect(self._update_component_data)

        self._mediator.bearingChanged.connect(self._on_bearing_changed)

    def _update_component_data(self, tab_id, data):
        self._calculator.update_data(data)

        if tab_id == 1:
            self._on_update_preliminary_data()
        elif tab_id == 2:
            self._on_update_bearings_data()
        elif tab_id == 3:
            self._on_update_power_loss_data()

    def _open_shaft_designer_window(self):
        self._shaft_designer.show()

    def _on_select_materials(self):
        """
        Open selection of shaft material from database
        """
        if self.db_controller.show_materials():
            self.tab_controllers[0].on_materials_selected(self.db_controller.data)
    
    def _on_select_bearing_type(self, bearing_section_id):
        """
        Open selection of bearing type from database

        Args:
            bearing_section_id (str): Id of section that specifies the bearing location.
        """
        support_type = 'centralne' if bearing_section_id == 'eccentrics' else 'podporowe'
        if self.db_controller.show_bearing_types(support_type):
            self.tab_controllers[1].on_bearing_type_selected(bearing_section_id, self.db_controller.data)

    def _on_select_bearing(self, bearing_section_id, data):
        """
        Open selection of bearing from database
        
        Args:
            bearing_section_id (str): Id of section that specifies the bearing location.
        """
        self._calculator.update_data(data)
        support_type = 'centralne' if bearing_section_id == 'eccentrics' else 'podporowe'
        bearing_type = self._calculator.get_bearing_type(bearing_section_id)
        limits = self._calculator.get_bearings_attributes_limits(bearing_section_id)
        if self.db_controller.show_bearings(support_type, bearing_type, *limits):
            self.tab_controllers[1].on_bearing_selected(bearing_section_id, self.db_controller.data)

    def _on_select_rolling_element(self, bearing_section_id, data):
        """
        Open selection of rolling element from database

        Args:
            bearing_section_id (str): Id of section that specifies the bearing location.
        """
        self._calculator.update_data(data)
        bearing_type = self._calculator.get_bearing_type(bearing_section_id)
        limits = self._calculator.get_rollings_element_limits(bearing_section_id)
        if self.db_controller.show_rolling_elements(bearing_type, limits):
            self.tab_controllers[2].on_rolling_element_selected(bearing_section_id, self.db_controller.data)

    def _on_update_preliminary_data(self):
        """
        Calculate attributes for the input shaft.

        :param data: Data used for calculating input shaft attributes.
        """
        self._shaft_designer_controller.update_shaft_data(self._calculator.get_data())

    def _on_update_bearings_data(self):
        self._calculator.calculate_bearings_attributes()

    def _on_update_power_loss_data(self):
        self._calculator.calculate_absolute_power_loss()

    def _on_bearing_changed(self, bearing_section_id, bearing_data):
        bearing_data = self._calculator.get_bearing_attributes(bearing_section_id, bearing_data)
        self._shaft_designer_controller.update_bearing_data(bearing_data)

    def _on_shaft_designing_finished(self):
        self._input_mechanism.handleShaftDesigningFinished()

    def save_data(self):
        '''
        Get the component data
        '''
        data = []
        # Get calculator data
        data.append(self._calculator.get_data())

        # Get shaft designer data
        data.append(self._shaft_designer_controller.get_shaft_data())

        # Get every tab data
        for tab_controller in self.tab_controllers[:-1]:
            data.append(tab_controller.get_data())

        # Get isShaftDesigned flag
        data.append(self._input_mechanism.isShaftDesigned)
        return data

    def load_data(self, data):
        '''
        Set the initial component data.
        '''
        # Set the calculators data
        self._calculator.set_data(data[0])
        self._calculator.set_initial_data()

        # Set the shaft designer data
        if data[1]:
            self._shaft_designer_controller.update_shaft_data(self._calculator.get_data())
            self._shaft_designer_controller.set_shaft_data(data[1])

        # Set every tab data
        for idx, tab_controller in enumerate(self.tab_controllers[:-1]):
            tab_controller.set_state(data[idx+2])
        
        # Set isShaftDesigned flag
        self._input_mechanism.isShaftDesigned = data[-1]
        if self._input_mechanism.isShaftDesigned:
            self._on_shaft_designing_finished()
