from PySide2.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QPushButton, QWidget, QHBoxLayout, QStackedLayout, QVBoxLayout, QAction, QGridLayout
from PySide2.QtGui import QIcon
from main_view import Animation_View
from pawel import Tab_Pawel
from wiktor import Tab_Wiktor
from milosz import Tab_Milosz
from kamil import Tab_Kamil
from eksportdanych import Eksport_Danych
import json
import re
from functools import partial


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

        self.pawel = Tab_Pawel(self)
        self.pawel.anim_data_updated.connect(self.update_animation_data)
        self.pawel.update_other_tabs.connect(lambda: self.activate_tab(0))

        self.wiktor = Tab_Wiktor(self)
        self.wiktor.data.anim_data_updated.connect(self.update_animation_data)
        milosz = Tab_Milosz(self)

        # Zapewnienie, że tylko jeden mechanizm wyjściowy będzie aktywny
        self.wiktor.enable_other.connect(milosz.use_this_changed)
        milosz.enable_other.connect(self.wiktor.use_this_changed)

        kamil = Tab_Kamil(self)
        eksport = Eksport_Danych(self, self.pawel.data.sily)

        main_layout = QGridLayout()
        data_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()
        animation_layout = QStackedLayout()

        self.animation_view = Animation_View(self, self.pawel.data.dane)
        animation_layout.addWidget(self.animation_view)
        self.animation_view.animacja.animation_tick.connect(self.on_animation_tick)

        data_layout.addLayout(button_layout)
        data_layout.addLayout(self.stacklayout)

        main_layout.addLayout(animation_layout,0,0,1,4)
        main_layout.addLayout(data_layout,0,4,1,2)

        self.tab_titles = ["Zarys", "Mechanizm Wyj I", "Mechanizm Wyj II", "Mechanizm Wej", "Eksport"]
        self.stacked_widgets = [self.pawel, self.wiktor, milosz, kamil, eksport]

        for index, (title, widget) in enumerate(zip(self.tab_titles, self.stacked_widgets)):
            button = QPushButton(title)
            button_layout.addWidget(button)
            self.stacklayout.addWidget(widget)
            button.pressed.connect(partial(self.activate_tab, index))
        
        #Menu główne:
        menu = self.menuBar()

        #FILE MENU :
        filemenu =menu.addMenu("&Plik")

        otworz = QAction("Otwórz",self)
        filemenu.addAction(otworz)
        otworz.triggered.connect(self.load_JSON)

        zapis = QAction("Zapisz",self)
        filemenu.addAction(zapis)
        zapis.setShortcut("Ctrl+S")
        zapis.triggered.connect(self.save_to_JSON)

        exit_app = QAction("Wyjście",self)
        filemenu.addAction(exit_app)
        exit_app.triggered.connect(self.closeApp)

        #EDIT MENU :
        editmenu = menu.addMenu("&Edycja")

        #PRZECHPDZENIE MIĘDZY SEKCJAMI MENU :
        sectionmenu = menu.addMenu("&Sekcja")

        for index, (title, widget) in enumerate(zip(self.tab_titles, self.stacked_widgets)):
            button = QAction(title, self)
            sectionmenu.addAction(button)
            button.triggered.connect(partial(self.activate_tab, index))

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
    
    def closeEvent(self, event):
        self.animation_view.start_event.clear()
        return super().closeEvent(event)
    
    def closeApp(self):
        self.animation_view.start_event.clear()
        exit()

    def activate_tab(self, index):
        previous = self.stacklayout.currentIndex()
        new_data = self.stacked_widgets[previous].send_data()
        for tab_widget in self.stacked_widgets:
            tab_widget.receive_data(new_data)

        self.stacklayout.setCurrentIndex(index)
    
    def on_animation_tick(self, kat):
        self.wiktor.data.inputs_modified(kat, self.wiktor.use_this_check.isChecked())
    
    def update_animation_data(self, dane):
        data = {'pawel': dane.get("pawel")}
        if dane.get("wiktor"):
            data.update({'wiktor': dane.get("wiktor")})
        self.animation_view.update_animation_data(data)

    def load_JSON(self):
        '''Wczytuje dane z pliku .json, wywołuje metodę load_data() każdej z zakładek, podając im słownik jej danych.
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
            tab.load_data(data.get(key))
        
    def save_to_JSON(self):
        '''Zapis do pliku JSON. Wywołuje na każdej zakładce metodę save_data(), zbiera zwrócone przez nie dane i zapisuje jako obiekty,
        których klucze są takie same, jak self.tab_titles.
        Wywołuje activate_tab(), żeby upewnić się, że przekazane są między nami dane, i wykonane obliczenia przed zapisem.

        Użycie tej metody, albo load_JSON(), zapisuje podaną przez użytkownika ścieżkę, i kolejne wywołania tej metody automatycznie zapisują do tego pliku.'''
        def save_ess(f_path, dane):
            try:
                with open(f_path, 'w') as f:
                    json.dump(dane, f)
                QMessageBox.information(self, 'Plik zapisany', 'Dane zostały zapisane do pliku JSON.')
                self.loaded_file = f_path
            except Exception as e:
                QMessageBox.critical(self, 'Błąd', f'Wystąpił błąd podczas zapisu do pliku: {str(e)}')

        self.activate_tab(0)
        self.activate_tab(1)
        data = { key: tab.save_data() for key, tab in zip(self.tab_titles, self.stacked_widgets)}
        if self.loaded_file is not None:
            save_ess(self.loaded_file, data)
            return

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setWindowTitle("Zapis")
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
