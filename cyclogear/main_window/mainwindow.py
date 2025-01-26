from functools import partial
import json
import math

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QPushButton, QWidget, QHBoxLayout, QStackedLayout, QVBoxLayout, QAction, QGridLayout, QDialog, QDialogButtonBox, QLabel

from .base_data_widget import BaseDataWidget
from .error_widget import ErrorWidget
from animation.animation_view import AnimationView
from modules.roller_output_mechanism.roller_mechanism import RollerOutTab
from modules.gear.gear_tab import GearTab
from common.utils import open_save_dialog
from modules.pin_output_mechanism.pin_mechanism import PinOutTab
from modules.input_mechanism.controller.input_mechanism_controller import InputMechanismController
from modules.input_mechanism.view.InputMechanism import InputMechanism
from modules.input_mechanism.model.input_mechanism_calculator import InputMechanismCalculator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Przekładnia Cykloidalna")
        self.setMinimumSize(1050,750)
        self.showMaximized()

        #ustawienie ikonki :
        main_icon = QIcon()
        main_icon.addFile("resources//images//mainwindow_icon.png")
        self.setWindowIcon(main_icon)

        self.loaded_file = None
        central_widget = QWidget()

        self.gear_tab = GearTab(central_widget)
        self.gear_tab.data.animDataUpdated.connect(self.updateAnimationData)

        self.pin_out_tab = PinOutTab(central_widget)
        self.pin_out_tab.data.animDataUpdated.connect(self.updateAnimationData)
        self.gear_tab.data.dane_materialowe.wheelMatChanged.connect(self.pin_out_tab.data.material_frame.changeWheelMat)

        roller_out_tab = RollerOutTab(central_widget)

        # Zapewnienie, że tylko jeden mechanizm wyjściowy będzie aktywny
        self.pin_out_tab.thisEnabled.connect(roller_out_tab.useOtherChanged)
        roller_out_tab.thisEnabled.connect(self.pin_out_tab.useOtherChanged)

        self.input_shaft_tab_controller = InputMechanismController(central_widget)

        main_layout = QGridLayout()
        data_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()
        animation_layout = QStackedLayout()

        self.animation_view = AnimationView(central_widget, self.gear_tab.data.dane_all.copy())
        animation_layout.addWidget(self.animation_view)
        # self.animation_view.animacja.animation_tick.connect(self.onAnimationTick)

        data_layout.addLayout(button_layout)
        data_layout.addLayout(self.stacklayout)

        main_layout.addLayout(animation_layout,0,1,1,6)
        main_layout.addLayout(data_layout,0,7,1,3)
        self.error_box = ErrorWidget(central_widget)
        self.error_box.show()
        self.pin_out_tab.data.errorsUpdated.connect(partial(self.error_box.updateErrors, module="PinOutTab"))
        self.gear_tab.data.errorsUpdated.connect(partial(self.error_box.updateErrors, module="GearTab"))
        self.error_box.resetErrors()

        self.base_data = BaseDataWidget(central_widget)
        self.base_data.dataChanged.connect(self.exchangeData)

        self.help_button = QPushButton(central_widget)
        self.help_button.setIcon(QIcon("resources//images//pomoc_zarys1.png"))
        self.help_button.setIconSize(QSize(140, 140))
        self.help_button.resize(150, 150)
        self.help_label = QLabel("Otwórz obrazek pomocniczy", self.help_button)
        self.help_label.move(10, 10)
        self.help_button.pressed.connect(self.helpClicked)

        self.tab_titles = ["Zarys", "Mechanizm Wyj I", "Mechanizm Wyj II", "Mechanizm Wej"]
        # self.stacked_widgets = [self.gear_tab, self.pin_out_tab, roller_out_tab]
        self.stacked_widgets = [self.gear_tab, self.pin_out_tab, roller_out_tab, self.input_shaft_tab_controller]

        for index, (title, widget) in enumerate(zip(self.tab_titles, self.stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button)
            self.stacklayout.addWidget(widget.getView())
            widget.dataChanged.connect(self.exchangeData)
            button.pressed.connect(partial(self.activateTab, index))
        
        #Menu główne:
        menu = self.menuBar()
        filemenu = menu.addMenu("&Plik")

        otworz = QAction("Otwórz",self)
        filemenu.addAction(otworz)
        otworz.triggered.connect(self.loadJSON)

        zapis = QAction("Zapisz",self)
        filemenu.addAction(zapis)
        zapis.setShortcut("Ctrl+S")
        zapis.triggered.connect(self.saveToJSON)

        zapis_jako = QAction("Zapisz jako",self)
        filemenu.addAction(zapis_jako)
        zapis_jako.triggered.connect(lambda: self.saveToJSON("save as"))

        #EKSPORTY :
        eksport_menu = menu.addMenu("&Eksport")

        raport = QAction("Generuj raport", self)
        eksport_menu.addAction(raport)
        raport.triggered.connect(self.generateRaport)

        eksport_csv = QAction("Eksport wykresów", self)
        eksport_menu.addAction(eksport_csv)
        eksport_csv.triggered.connect(self.generateCSV)

        eksport_dxf = QAction("Eksport do DXF", self)
        eksport_menu.addAction(eksport_dxf)
        eksport_dxf.triggered.connect(self.generateDXF)

        #PRZECHODZENIE MIĘDZY SEKCJAMI MENU :
        sectionmenu = menu.addMenu("&Sekcja")

        for index, (title, widget) in enumerate(zip(self.tab_titles, self.stacked_widgets)):
            button = QAction(title, self)
            sectionmenu.addAction(button)
            button.triggered.connect(partial(self.activateTab, index))

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def resizeEvent(self, event) -> None:
        try:
            w, h = self.animation_view.size().toTuple()
            self.help_button.move(w-150, 20)
            self.base_data.move(w-200, h-170)
        except AttributeError:
            # pierwsze ustalenie rozmiaru okna, jeszcze nie ma animation view.
            pass
        return super().resizeEvent(event)

    def helpClicked(self):
        btn_size = self.help_button.size()
        btn_pos = self.help_button.pos()
        if btn_size.width() == 150:
            self.help_button.move(btn_pos.x() - 450, 20)
            self.help_button.resize(600, 600)
            self.help_button.setIconSize(QSize(590, 590))
            self.help_label.hide()
        else:
            self.help_button.move(btn_pos.x() + 450, 20)
            self.help_button.resize(150, 150)
            self.help_button.setIconSize(QSize(140, 140))
            self.help_label.show()

    def closeEvent(self, event):
        dialog = QDialog(self, Qt.WindowCloseButtonHint)
        dialog.setWindowTitle("Zapisać zmiany?")
        label = QLabel("Czy chcesz zapisać zmiany?")
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Discard | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Save).clicked.connect(lambda: dialog.done(2))
        button_box.button(QDialogButtonBox.Save).setText("Zapisz")
        button_box.button(QDialogButtonBox.Discard).clicked.connect(lambda: dialog.done(1))
        button_box.button(QDialogButtonBox.Discard).setText("Odrzuć zmiany")
        button_box.button(QDialogButtonBox.Cancel).clicked.connect(lambda: dialog.done(0))
        button_box.button(QDialogButtonBox.Cancel).setText("Anuluj")
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        choice = dialog.exec_()
        if choice == 2:
            self.saveToJSON()
            self.animation_view.closeEvent(event)
            return super().closeEvent(event)
        elif choice == 1:
            self.animation_view.closeEvent(event)
            return super().closeEvent(event)
        elif choice == 0:
            event.ignore()

    def activateTab(self, index):
        old_index = self.stacklayout.currentIndex()
        if old_index == 0 or old_index == 1:
            self.stacked_widgets[old_index].data.recalculate()
        
        self.stacklayout.setCurrentIndex(index)
        self.help_button.show()
        if index == 0:
            self.help_button.setIcon(QIcon("resources//images//pomoc_zarys1.png"))
        elif index == 1:
            self.help_button.setIcon(QIcon("resources//images//pomoc_mechanizm_I.bmp"))
        else:
            self.help_button.hide()
    
    def exchangeData(self, passed_data):
        for tab_widget in self.stacked_widgets:
            tab_widget.receiveData(passed_data)
    
    def onAnimationTick(self, kat):
        self.pin_out_tab.data.recalculate(kat)
    
    def updateAnimationData(self, dane):
        self.animation_view.animation.updateData(dane)

    def generateRaport(self):
        if self.error_box.errorsExist():
            QMessageBox.critical(self, 'Błąd', 'Przed generowaniem raportu, pozbądź się błędów.')
            return
        
        file_path = open_save_dialog(".rtf")
        if not file_path:
            return
        # file_name = "CycloRaport_" + datetime.datetime.today().strftime('%d-%m-%Y_%H-%M-%S') + ".rtf"
        try:
            with open(file_path, 'w') as f:
                f.write("{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}\\f0\\fs20")
                f.write("{\\pard\\qc\\b Raport \\line\\par}")
                f.write(self.base_data.reportData())
                for tab_widget in self.stacked_widgets:
                    f.write(tab_widget.reportData())
                f.write("}")
            QMessageBox.information(self, 'Raport zapisany', 'Raport został utworzony.')
        except Exception as e:
            QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd podczas tworzenia raportu: {str(e)}')

    def generateCSV(self):
        if self.error_box.errorsExist():
            QMessageBox.critical(self, 'Błąd', 'Przed generowaniem csv, pozbądź się błędów.')
            return
        
        file_path = open_save_dialog(".csv")
        if not file_path:
            return
        # file_name = "CycloWykresy_" + datetime.datetime.today().strftime('%d-%m-%Y_%H-%M-%S') + ".csv"
        try:
            with open(file_path, "w") as f:
                for tab_widget in self.stacked_widgets:
                    f.write(tab_widget.csvData())
            QMessageBox.information(self, 'Tabele zapisane', 'Utworzono plik CSV z danymi.')
        except Exception as e:
            QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd podczas tworzenia pliku csv: {str(e)}')

    def generateDXF(self):
        if self.error_box.errorsExist():
            QMessageBox.critical(self, 'Błąd', 'Przed generowaniem rysunku, pozbądź się błędów.')
            return
        
        file_path = open_save_dialog(".dxf")
        if not file_path:
            return
        # file_name = "CycloRysunek_" + datetime.datetime.today().strftime('%d-%m-%Y_%H-%M-%S') + ".dxf"
        try:
            with open(file_path, "w") as f:
                # TODO generowanie dxf nie jest 100% pewne. przy range(720), psuje się dla parzystego przełożenia.
                f.write("0\nSECTION\n2\nENTITIES\n")

                data = ''
                z, ro = self.gear_tab.data.dane_all["z"], self.gear_tab.data.dane_all["ro"]
                h, g = self.gear_tab.data.dane_all["lam"], self.gear_tab.data.dane_all["g"]
                e = self.gear_tab.data.dane_all["e"]
                Rg = self.gear_tab.data.dane_all["Rg"]

                wheel_layer_name = "zarys"

                data += f"0\nPOLYLINE\n8\n{wheel_layer_name}\n66\n1\n"
                # TODO: dokładniejsza konwersja na radiany` jest konieczna, żeby nie było drobnych błędów, przecinania kół.
                for j in range(0, 1440):
                    i = j / 4
                    x = (ro * (z + 1) * math.cos(i * 0.01745329)) - (h * ro * (math.cos((z + 1) * i * 0.01745329))) - ((g * ((math.cos(i * 0.01745329) - (h * math.cos((z + 1) * i * 0.01745329))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.01745329)) + (h * h))))))
                    y = (ro * (z + 1) * math.sin(i * 0.01745329)) - (h * ro * (math.sin((z + 1) * i * 0.01745329))) - ((g * ((math.sin(i * 0.01745329) - (h * math.sin((z + 1) * i * 0.01745329))) / (math.sqrt(1 - (2 * h * math.cos(z * i * 0.01745329)) + (h * h))))))
                    # zarys przesuniety o mimosrod
                    data += f"0\nVERTEX\n8\n{wheel_layer_name}\n10\n{x+e}\n20\n{y}\n"
                data += f"0\nSEQEND\n8\n{wheel_layer_name}\n"

                layer_name = "rolki"
                angle_step = 360 / (z+1)
                for i in range(z+1):
                    x = Rg * math.cos(i * angle_step * 0.01745329)
                    y = Rg * math.sin(i * angle_step * 0.01745329)
                    data += f"0\nCIRCLE\n8\n{layer_name}\n10\n{x}\n20\n{y}\n40\n{g}\n"
                
                layer_name = "osie"
                # axes extend beyond the mechanism by a small distance for readability. The distance == g (roller radius).
                data += f"0\nLINE\n8\n{layer_name}\n10\n{-(Rg+2*g)}\n20\n0\n11\n{Rg+2*g}\n21\n0\n"
                data += f"0\nLINE\n8\n{layer_name}\n10\n0\n20\n{-(Rg+2*g)}\n11\n0\n21\n{Rg+2*g}\n"
                data += f"0\nLINE\n8\n{layer_name}\n10\n{e}\n20\n{-(Rg+2*g)}\n11\n{e}\n21\n{Rg+2*g}\n"
                data += f"0\nCIRCLE\n8\n{layer_name}\n10\n0\n20\n0\n40\n{Rg}\n"

                if self.pin_out_tab.use_this_check.isChecked():
                    radius, bushings_count = self.pin_out_tab.data.input_dane["R_wt"], self.pin_out_tab.data.input_dane["n"]
                    pin_diameter, bushing_diameter = self.pin_out_tab.data.input_dane["d_sw"], self.pin_out_tab.data.input_dane["d_tul"]
                    hole_diameter = self.pin_out_tab.data.obliczone_dane["d_otw"]

                    layer_name = "mechanizm_wyjsciowy"
                    for i in range(bushings_count):
                        bushing_angle = (2 * math.pi * i) / bushings_count
                        x = radius * math.cos(bushing_angle)
                        y = radius * math.sin(bushing_angle)

                        data += f"0\nCIRCLE\n8\n{wheel_layer_name}\n10\n{x+e}\n20\n{y}\n40\n{hole_diameter/2}\n"
                        data += f"0\nCIRCLE\n8\n{layer_name}\n10\n{x}\n20\n{y}\n40\n{bushing_diameter/2}\n"
                        data += f"0\nCIRCLE\n8\n{layer_name}\n10\n{x}\n20\n{y}\n40\n{pin_diameter/2}\n"
                
                f.write(data)
                f.write("0\nENDSEC\n0\nEOF\r")
            QMessageBox.information(self, 'Rysunek zapisany', 'Utworzono rysunek zarysu.')
        except Exception as e:
            QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd podczas tworzenia rysunku: {str(e)}')

    def loadJSON(self):
        '''Wczytuje dane z pliku .json, wywołuje metodę loadData() każdej z zakładek, podając im słownik jej danych.
        Może być None, każdy musi z osobna sprawdzić przed odczytywaniem pojedynczych pozycji.'''
        data = None
        file_path = None
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setWindowTitle("Wczytywanie danych")
        file_dialog.setNameFilter('JSON Files (*.json)')

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                QMessageBox.information(self, 'Dane wczytane', 'Dane zostały wczytane.')
            except Exception as e:
                QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd przy wczytywaniu pliku: {str(e)}')
        
        if data is None or list(data.keys()) != self.tab_titles:
            # QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd przy wczytywaniu pliku.')
            return
        
        self.loaded_file = file_path
        self.base_data.loadData(data.get("base"))
        for key, tab in zip(self.tab_titles, self.stacked_widgets):
            tab.loadData(data.get(key))
        
    def saveToJSON(self, mode="save"):
        '''Zapis do pliku JSON. Wywołuje na każdej zakładce metodę saveData(), zbiera zwrócone przez nie dane i zapisuje jako obiekty,
        których klucze są takie same, jak self.tab_titles.
        Wywołuje activateTab(), żeby upewnić się, że przekazane są między nami dane, i wykonane obliczenia przed zapisem.

        Użycie tej metody, albo loadJSON(), zapisuje podaną przez użytkownika ścieżkę, i kolejne wywołania tej metody automatycznie zapisują do tego pliku.'''
        def save_ess(f_path, dane):
            try:
                with open(f_path, 'w') as f:
                    json.dump(dane, f)
                QMessageBox.information(self, 'Plik zapisany', 'Dane zostały zapisane do pliku JSON.')
                self.loaded_file = f_path
            except Exception as e:
                QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd podczas zapisu do pliku: {str(e)}')

        data = { key: tab.saveData() for key, tab in zip(self.tab_titles, self.stacked_widgets)}
        data.update({"base": self.base_data.saveData()})
        if self.loaded_file is not None and mode != "save as":
            save_ess(self.loaded_file, data)
            return
        
        file_path = open_save_dialog(".json")
        if file_path:
            save_ess(file_path, data)
