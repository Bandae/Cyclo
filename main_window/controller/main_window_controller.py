import math
from functools import partial

from main_window.view.main_window import MainWindow
from main_window.model.session_manager import SessionManager
from main_window.model.generator import Generator

from tabs.gear.view.gear_tab import GearTab
from tabs.gear.controller.gear_tab_controller import GearTabController

from tabs.pin_out.view.pin_out_tab import PinOutTab
from tabs.pin_out.controller.pin_out_tab_controller import PinOutTabController

from tabs.output_mechanism.output_mechanism_tab import OutputMechanismTab
from tabs.output_mechanism.output_mechanism_tab_controller import OutputMechanismTabController

from tabs.input_shaft.input_shaft_tab import InputShaftTab
from tabs.input_shaft.input_shaft_controller import InputShaftTabController

from common.message_handler import MessageHandler

class MainWindowController:
    def __init__(self, main_window: MainWindow):
        self._main_window = main_window
        
        self._session_manager = SessionManager(self._main_window)
        self._generator = Generator(self._main_window)

        self._init_components()
        self._connect_signals_and_slots()

    def _init_components(self):
        self.components = {}

        # Init Gear component
        self.gear_tab = GearTab()
        self.gear_tab_controller = GearTabController(self.gear_tab)
        self.components['Zarys'] = (self.gear_tab, self.gear_tab_controller)

        # Init PinOut component
        self.pin_out_tab = PinOutTab()
        self.pin_out_tab_controller = PinOutTabController(self.pin_out_tab)
        self.components['Mechanizm Wyj I'] = (self.pin_out_tab, self.pin_out_tab_controller)

        # Init OutputMechanism component
        self.output_mechanism_tab = OutputMechanismTab()
        self.output_mechanism_tab_controller = OutputMechanismTabController(self.output_mechanism_tab)
        self.components['Mechanizm Wyj II'] = (self.output_mechanism_tab, self.output_mechanism_tab_controller)

        # Init InputShaft component
        self.input_shaft_tab = InputShaftTab()
        self.input_shaft_tab_controller = InputShaftTabController(self.input_shaft_tab)
        self.components['Mechanizm Wej'] = (self.input_shaft_tab, self.input_shaft_tab_controller)

        self._main_window.set_tabs({key: value[0] for key, value in self.components.items()})

    def _connect_signals_and_slots(self):
        self._main_window.otworz.triggered.connect(self.loadData)
        self._main_window.zapis.triggered.connect(self.saveData)
        self._main_window.zapis_jako.triggered.connect(lambda: self.saveData("save as"))

        self._main_window.raport.triggered.connect(self.generateRaport)
        self._main_window.eksport_csv.triggered.connect(self.generateCSV)
        self._main_window.eksport_dxf.triggered.connect(self.generateDXF)

        for component in self.components.values():
            component[0].dataChanged.connect(self.exchangeData)

        self._main_window.base_data.dataChanged.connect(self.exchangeData)

        self.gear_tab.data.animDataUpdated.connect(self._main_window.updateAnimationData)
        self.gear_tab.data.dane_materialowe.wheelMatChanged.connect(self.pin_out_tab.data.material_frame.changeWheelMat)
        self.gear_tab.data.errorsUpdated.connect(partial(self._main_window.error_box.updateErrors, module="GearTab"))

        self.pin_out_tab.data.animDataUpdated.connect(self._main_window.updateAnimationData)
        self.pin_out_tab.thisEnabled.connect(self.output_mechanism_tab.useOtherChanged)
        self.pin_out_tab.data.errorsUpdated.connect(partial(self._main_window.error_box.updateErrors, module="PinOutTab"))

        self.output_mechanism_tab.this_enabled.connect(self.pin_out_tab.useOtherChanged)

    def exchangeData(self, passed_data):
        for component in self.components.values():
            component[1].receiveData(passed_data)

    def loadData(self):
        data = self._session_manager.loadJSON()
        
        if data is None or list(data.keys()) != list[self.components.keys()]:
            MessageHandler.critical(self._main_window, 'Błąd', f'Wystąpił błąd przy wczytywaniu pliku.')
            return
        
        self._main_window.base_data.loadData(data.get("base"))
        for tittle, component in self.components.items():
            component[1].loadData(data.get(tittle))

    def saveData(self, mode):
        data = { tittle: component[1].saveData() for tittle, component in self.components.items()}
        data.update({"base": self._main_window.base_data.saveData()})

        self._session_manager.saveToJSON(data, mode)
        
    def generateRaport(self):
        if self._main_window.error_box.errorsExist():
            MessageHandler.critical(self._main_window, 'Błąd', 'Przed generowaniem raportu, pozbądź się błędów.')
            return
        
        report_data = self._main_window.base_data.reportData()
        
        for component in self.components.values():
            report_data += component[1].reportData()
        
        self._generator.generateRaport(report_data)

    def generateCSV(self):
        if self._main_window.error_box.errorsExist():
            MessageHandler.critical(self._main_window, 'Błąd', 'Przed generowaniem csv, pozbądź się błędów.')
            return
        
        csv_data = ''
        for component in self.components.values():
                   csv_data += component[1].csvData()
                    
        self._generator.generateCSV(csv_data)

    def generateDXF(self):
        if self._main_window.error_box.errorsExist():
            MessageHandler.critical(self._main_window, 'Błąd', 'Przed generowaniem rysunku, pozbądź się błędów.')
            return
        
        data = ''
        z, ro = self.gear_tab.data.dane_all["z"], self.gear_tab.data.dane_all["ro"]
        h, g = self.gear_tab.data.dane_all["lam"], self.gear_tab.data.dane_all["g"]

        for j in range(0, 720):
            i= j / 2
            x = (ro * (z + 1) * math.cos(i * 0.0175)) - (h * ro * (math.cos((z + 1) * i * 0.0175))) - ((g * ((math.cos(i * 0.0175) - (h * math.cos((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
            y = (ro * (z + 1) * math.sin(i * 0.0175)) - (h * ro * (math.sin((z + 1) * i * 0.0175))) - ((g * ((math.sin(i * 0.0175) - (h * math.sin((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
            data += f"10\n{x}\n20\n{y}\n"

        self._generator.generateDXF(data)
