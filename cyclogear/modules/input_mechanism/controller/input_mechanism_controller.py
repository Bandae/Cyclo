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

from modules.shaft_designer.view.ShaftDesigner import ShaftDesigner
from modules.shaft_designer.controller.shaft_designer_controller import ShaftDesignerController

from db_handler.controller.db_controller import DbController
from db_handler.model.db_handler import DbHandler
from db_handler.view.DbItemsWindow import DbItemsWindow

from modules.common.abstract_tab import AbstractTab
import math

class InputMechanismController(AbstractTab):
    """
    Controller for the InputMechanism in the application.

    This class handles the interactions between the model (data) and the view (InputMechanism),
    including initializing the view with data, connecting signals and slots, and handling
    user interactions.
    """
    def __init__(self, parent_for_view):
        """
        Initialize the InputMechanismController.

        :param data: The data for the application.
        :param view: The InputMechanism (QWidget) instance of the input shaft coomponent's GUI.
        """
        super().__init__()
        self._input_mechanism = InputMechanism(parent_for_view)
        self._calculator = InputMechanismCalculator()

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
    
    # ---------- methods used for interactions with other modules and main window ----------

    def receiveData(self, new_data):
        # TODO
        # isShaftDesigned -- ta flaga jest chyba tylko ustawiana. Nie resetuje się nawet jak zostaną tak zmienione dane w pierwszej zakładce, że wał należy przeprojektować.
        # zmiana łożyska nie zmienia od razu, tylko jeśli sie przełączy na zakładke strat mocy.
        # r_mr z zakładki mech_wyj chyba nigdzie nie jest używane. A powinno być.
        # powrót do poprzedniego input i wpisanie innej wartości nie poprawia dalej limitów
        # kiedy już się dojdzie pierwszy raz do którejś zakładki to jest "odblokowana" i nawet jak coś sie zmieni wcześniej i np. poprzednia zakładka jest niewypełniona - to nadal jest dostęp do tej następnej.

        wanted_data = None
        if new_data.get("GearTab") is not None: # rw1, B, n, e, Fwzx, Fwzy, n
            wanted_data = new_data.get("GearTab")
            self._calculator.update_data({
                'Fwzx': [wanted_data["Fwzx"], 'N'],
                'Fwzy': [wanted_data["Fwzy"], 'N'],
                'n': [wanted_data["K"], ''],
                'B': [wanted_data["B"], 'mm'],
                'rw1': [wanted_data["R_w1"], 'mm'],
                'e': [wanted_data["e"], 'mm']
            })

            self._calculator.set_initial_data() # to tylko przelicza na podstawie nowych danych zależne od nich dane w kalkulatorze. Trzeba jeszcze je wpisać w view.
            self.tabs[0]._outputs["B"][0].setValue(wanted_data["B"]) # zakladka pierwsza
            self.tabs[0]._outputs["e"][0].setValue(wanted_data["e"]) # atrybuty łożysk w input_mech_calc, łączna strata mocy w łożyskach w ostatniej zakładce
            self.tab_controllers[0].update_state()

            # rw1, e -- zmienia straty mocy w łożyskach.
            for section_id in ['support_A', 'support_B', 'eccentrics']:
                # Zakłada, że straty się zmienią tylko jeśli zmieni się f, znormalizowana średnica, lub zmieni się łożysko w poprzedniej zakładce.
                # reasumując - muszę zrobić przeliczenie tylko jeśli jest wypełniona dana sekcja. Jeśli nie jest, to i tak będzie musiała być przeliczona później, a wtedy zaciągnie już nowe dane.
                # czy jest wypełniona mogę wiedzieć używając metody checkStatus z klasy ITrackedWidget (bo dziedziczy ją ten element)
                # Jednak ten element nie jest przypisany do klasy więc nie ma do niego dostępu z zewnątrz, odniesienia. Może jakoś jest przez ten ITrackedTab, ale nie rozumiem tego. Więc zapisałem odniesienie w atrybucie dataSubsections
                if self.tabs[2].dataSubsections[section_id].checkStatus()[0]:
                    self.tab_controllers[2]._on_rolling_element_data_provided(section_id, True, True)
            
            self.tab_controllers[3].update_state()

        elif new_data.get("base") is not None:
            wanted_data = new_data.get("base")
            # nwe -- zmienia nośność łożysk - calculate_bearing_load_capacity. Poza tym w ostatniej zakładce jest wyświetlane.
            self._calculator.update_data({'nwe': [wanted_data["n_wej"], 'obr/min']})
            for section_id in ['support_A', 'support_B', 'eccentrics']:
                if self.tabs[1].sections_reference[section_id].checkStatus()[0]:
                    self.tab_controllers[1]._on_bearing_data_provided(section_id, True, True)
            
            # w0 -- obliczyc z nwe -- zmienia straty mocy - calculate_bearing_power_loss
            self._calculator.update_data({'w0': [math.pi*wanted_data["n_wej"]/30, 'rad/s']})
            if self.tabs[2].dataSubsections[section_id].checkStatus()[0]:
                self.tab_controllers[2]._on_rolling_element_data_provided(section_id, True, True)

            # Mwe -- tylko w ostatniej zakladce wyswietlane, trzeba policzyc na podstawie przelozenia i Mwyj
            self._calculator.update_data({'Mwe': [wanted_data["M_wyj"] / wanted_data["i"], 'obr/min']})
            self.tab_controllers[3].update_state()
        elif new_data.get("PinOutTab") is not None: # F_wmr, r_mr, x
            wanted_data = new_data.get("PinOutTab")
            self._calculator.update_data({
                'Fwm': [wanted_data["Fwm"], 'N'],
                'x': [wanted_data["x"], 'mm'],
            })

            self._calculator.set_initial_data()
            self.tabs[0]._outputs["x"][0].setValue(wanted_data["x"])
            self.tab_controllers[0].update_state()
            self.tab_controllers[3].update_state()

        # Wszystkie nowe dane należy najpierw wpisać do głównego słownika z danymi przez self._calculator.update_data()
        #       niestety, trzeba podawać jednostki; wpisywanie bezpośrednio wartości do 0-wego elementu jest wątpliwe, bo obchodzi wewnętrzne funkcje tego modułu do zarządzania danymi (fetch_data_subset)
        #       dodatkowo:  F_wmr, Fwzx, Fwzy -- zależą od nich inne dane w kalkulatorze. Należy wywołać self._calculator.set_initial_data()
        
        # 1) self.tabs[0]._outputs["..."][0].setValue(...)
        #       3 dane wyświetlane na początku modułu. Trzeba je ręcznie aktualizować (bo założono, że sie nie zmieniają)
        #       Potrzebna po: B, x, e.

        # 2) self.tab_controllers[0].update_state()
        #       Ta metoda poprawia min-maxy w pierwszej zakładce, i czyści pola które się w nowych nie mieszczą, oraz wszystko za nimi.
        #       Potrzebna po: B, x, e. Możliwe, że po F_wmr, Fwzx, Fwzy też.

        # 3) przejście po sub-sekcjach zakładki łożysk, wywołanie _on_bearing_data_provided.
        #       Zewnętrzne dane wpływają na nośność - C. Wykonać ponownie obliczenia trzeba więc tylko jeśli wszystko do nośności jest już podane, a ona obliczona.
        #       Aby sprawdzić, czy wszystko jest podane w subsekcji, dodałem odnośnik sections_reference.
        #       Potrzebne po: nwe

        # 4) przejście po sub-sekcjach zakładki strat mocy, wywołanie _on_rolling_element_data_provided.
        #       Analogicznie do 2), odnośnik == dataSubsections
        #       Potrzebne po: rw1, e, w0

        # 5) self.tab_controllers[3].update_state()
        #       Aktualizacja wyników
    
    def getView(self):
        return self._input_mechanism
