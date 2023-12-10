from PySide2.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QPushButton, QWidget, QHBoxLayout, QStackedLayout, QVBoxLayout, QAction, QGridLayout, QDialog, QDialogButtonBox, QLabel
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt
from main_view import AnimationView
from pawel import Tab_Pawel
from wiktor import TabWiktor
from milosz import Tab_Milosz
from kamil import Tab_Kamil
from error_widget import ErrorWidget
import json
import re
import datetime
from functools import partial

# TODO: moze jedna metode zrobic z tego wszystkiego do generowaniaa raport csv dxf


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Przekładnia Cykloidalna")
        self.setMinimumSize(1050,750)
        self.showMaximized()

        #ustawienie ikonki :
        main_icon = QIcon()
        main_icon.addFile("icons//mainwindow_icon.png")
        self.setWindowIcon(main_icon)

        self.loaded_file = None
        central_widget = QWidget()

        self.pawel = Tab_Pawel(central_widget)
        self.pawel.anim_data_updated.connect(self.updateAnimationData)
        self.pawel.update_other_tabs.connect(lambda: self.activateTab(0))

        self.wiktor = TabWiktor(central_widget)
        self.wiktor.data.anim_data_updated.connect(self.updateAnimationData)

        milosz = Tab_Milosz(central_widget)

        # Zapewnienie, że tylko jeden mechanizm wyjściowy będzie aktywny
        self.wiktor.this_enabled.connect(milosz.useOtherChanged)
        milosz.this_enabled.connect(self.wiktor.useOtherChanged)

        kamil = Tab_Kamil(self)

        main_layout = QGridLayout()
        data_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()
        animation_layout = QStackedLayout()

        self.animation_view = AnimationView(central_widget, self.pawel.data.dane_all)
        animation_layout.addWidget(self.animation_view)
        self.animation_view.animacja.animation_tick.connect(self.onAnimationTick)

        data_layout.addLayout(button_layout)
        data_layout.addLayout(self.stacklayout)

        main_layout.addLayout(animation_layout,0,1,1,6)
        main_layout.addLayout(data_layout,0,7,1,3)
        self.error_box = ErrorWidget(central_widget)
        self.error_box.show()
        self.wiktor.data.errors_updated.connect(self.error_box.updateErrors)
        self.error_box.resetErrors()

        self.tab_titles = ["Zarys", "Mechanizm Wyj I", "Mechanizm Wyj II", "Mechanizm Wej"]
        self.stacked_widgets = [self.pawel, self.wiktor, milosz, kamil]

        for index, (title, widget) in enumerate(zip(self.tab_titles, self.stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button)
            self.stacklayout.addWidget(widget)
            button.pressed.connect(partial(self.activateTab, index))
        
        #Menu główne:
        menu = self.menuBar()

        #FILE MENU :
        filemenu =menu.addMenu("&Plik")

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

        # eksport_dxf = QAction("Eksport do DXF", self)
        # eksport_menu.addAction(eksport_dxf)
        # eksport_dxf.triggered.connect(self.generateDXF)

        #PRZECHPDZENIE MIĘDZY SEKCJAMI MENU :
        sectionmenu = menu.addMenu("&Sekcja")

        for index, (title, widget) in enumerate(zip(self.tab_titles, self.stacked_widgets)):
            button = QAction(title, self)
            sectionmenu.addAction(button)
            button.triggered.connect(partial(self.activateTab, index))

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
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
            self.animation_view.start_event.clear()
            return super().closeEvent(event)
        elif choice == 1:
            self.animation_view.start_event.clear()
            return super().closeEvent(event)
        elif choice == 0:
            event.ignore()

    def activateTab(self, index):
        previous = self.stacklayout.currentIndex()
        new_data = self.stacked_widgets[previous].sendData()
        for tab_widget in self.stacked_widgets:
            tab_widget.receiveData(new_data)

        self.stacklayout.setCurrentIndex(index)
    
    def onAnimationTick(self, kat):
        self.wiktor.data.inputsModified(kat, self.wiktor.use_this_check.isChecked())
        self.pawel.data.obliczenia_sil(kat)
    
    def updateAnimationData(self, dane):
        data = {'pawel': dane.get("pawel")}
        if dane.get("wiktor"):
            data.update({'wiktor': dane.get("wiktor")})
        self.animation_view.updateAnimationData(data)

    def generateRaport(self):
        if self.error_box.errorsExist():
            QMessageBox.critical(self, 'Błąd', 'Przed generowaniem raportu, pozbądź się błędów.')
            return
        file_name = "CycloRaport_" + datetime.today().strftime('%d.%m.%Y_%H:%M:%S') + ".rtf"
        try:
            with open(file_name, 'w') as f:
                f.write("{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Lato;}}\\f0\\fs24")
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
        file_name = "CycloWykresy_" + datetime.today().strftime('%d.%m.%Y_%H:%M:%S') + ".csv"
        try:
            with open(file_name, "w") as f:
                for tab_widget in self.stacked_widgets:
                    f.write(tab_widget.csvData())
            QMessageBox.information(self, 'Tabele zapisane', 'Utworzono plik CSV z danymi.')
        except Exception as e:
            QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd podczas tworzenia pliku csv: {str(e)}')

    def generateDXF(self):
        ...

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

        self.activateTab(0)
        self.activateTab(1)
        data = { key: tab.saveData() for key, tab in zip(self.tab_titles, self.stacked_widgets)}
        if self.loaded_file is not None and mode != "save as":
            save_ess(self.loaded_file, data)
            return
        
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setWindowTitle("Zapis")
        file_dialog.setLabelText(QFileDialog.Accept, "Zapisz")
        file_dialog.setNameFilter('JSON Files (*.json)')

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            file_name = re.search(r"/([^\s\./]+)(\.[^\s\./]+)?$", file_path)
            if file_name is None or file_name.group(1) is None:
                QMessageBox.critical(self, 'Błąd', f'Niepoprawna nazwa pliku.')
                return
            elif file_name.group(2) != ".json":
                file_path += '.json'

            save_ess(file_path, data)
