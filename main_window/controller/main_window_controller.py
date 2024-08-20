import math
from PySide2.QtWidgets import QMessageBox

from main_window.view.main_window import MainWindow
from main_window.model.session_manager import SessionManager
from main_window.model.generator import Generator

class MainWindowController:
    def __init__(self, main_window: MainWindow):
        self._main_window = main_window
        
        self._session_manager = SessionManager(self._main_window)
        self._generator = Generator(self._main_window)

        self.connect_signals_and_slots()

    def connect_signals_and_slots(self):
        self._main_window.otworz.triggered.connect(self.loadData)
        self._main_window.zapis.triggered.connect(self.saveData)
        self._main_window.zapis_jako.triggered.connect(lambda: self.saveData("save as"))

        self._main_window.raport.triggered.connect(self.generateRaport)
        self._main_window.eksport_csv.triggered.connect(self.generateCSV)
        self._main_window.eksport_dxf.triggered.connect(self.generateDXF)

    def loadData(self):
        data = self._session_manager.loadJSON()
        
        if data is None or list(data.keys()) != self._main_window.tab_titles:
            QMessageBox.critical(self._main_window, 'Błąd', f'Wystąpił błąd przy wczytywaniu pliku.')
            return
        
        self._main_window.base_data.loadData(data.get("base"))
        for key, tab in zip(self._main_window.tab_titles, self._main_window.tab_widgets):
            tab.loadData(data.get(key))

    def saveData(self, mode):
        data = { key: tab_controller.saveData() for key, tab_controller in zip(self._main_window.tab_titles, self._main_window.tab_controllers)}
        data.update({"base": self._main_window.base_data.saveData()})

        self._session_manager.saveToJSON(data, mode)
        
    def generateRaport(self):
        if self._main_window.error_box.errorsExist():
            QMessageBox.critical(self._main_window, 'Błąd', 'Przed generowaniem raportu, pozbądź się błędów.')
            return
        
        report_data = self._main_window.base_data.reportData()
        
        for tab_controller in self._main_window.tab_controllers:
            report_data += tab_controller.reportData()
        
        self._generator.generateRaport(report_data)

    def generateCSV(self):
        if self._main_window.error_box.errorsExist():
            QMessageBox.critical(self._main_window, 'Błąd', 'Przed generowaniem csv, pozbądź się błędów.')
            return
        
        csv_data = ''
        for tab_controller in self._main_window.tab_controllers:
                   csv_data += tab_controller.csvData()
                    
        self._generator.generateCSV(csv_data)

    def generateDXF(self):
        if self._main_window.error_box.errorsExist():
            QMessageBox.critical(self._main_window, 'Błąd', 'Przed generowaniem rysunku, pozbądź się błędów.')
            return
        
        data = ''
        z, ro = self._main_window.gear_tab_controller.tab.data.dane_all["z"], self._main_window.gear_tab_controller.tab.data.dane_all["ro"]
        h, g = self._main_window.gear_tab_controller.tab.data.dane_all["lam"], self._main_window.gear_tab_controller.tab.data.dane_all["g"]

        for j in range(0, 720):
            i= j / 2
            x = (ro * (z + 1) * math.cos(i * 0.0175)) - (h * ro * (math.cos((z + 1) * i * 0.0175))) - ((g * ((math.cos(i * 0.0175) - (h * math.cos((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
            y = (ro * (z + 1) * math.sin(i * 0.0175)) - (h * ro * (math.sin((z + 1) * i * 0.0175))) - ((g * ((math.sin(i * 0.0175) - (h * math.sin((z + 1) * i * 0.0175))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.0175)) + (h * h))))))
            data += f"10\n{x}\n20\n{y}\n"

        self._generator.generateDXF(data)
