from PySide6.QtWidgets import QTabWidget,QMessageBox, QFileDialog, QMainWindow, QPushButton, QWidget, QHBoxLayout, QStackedLayout, QVBoxLayout
from PySide6.QtGui import QIcon, QAction
from main_view import Animation_View
from pawel import Tab_Pawel
from wiktor import Tab_Wiktor
from milosz import Tab_Milosz
from kamil import Tab_Kamil
from eksportdanych import Eksport_Danych
import json


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

        self.pawel = Tab_Pawel(self)
        kamil = Tab_Kamil()
        self.wiktor = Tab_Wiktor(self)
        milosz = Tab_Milosz()
        eksport = Eksport_Danych()

        main_layout = QHBoxLayout()
        data_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()
        animation_layout = QStackedLayout()

        self.animation_view = Animation_View(self, self.pawel.data.dane)
        animation_layout.addWidget(self.animation_view)

        data_layout.addLayout(button_layout)
        data_layout.addLayout(self.stacklayout)

        main_layout.addLayout(animation_layout)
        main_layout.addLayout(data_layout)

        tab_titles = ["Przekładnia Cykloidalna", "Mechanizm Wyjsciowy I", "Mechanizm Wyjsciowy II", "Mechanizm Wejsciowy", "Eksport danych"]
        stacked_widgets = [self.pawel, self.wiktor, milosz, kamil, eksport]
        buttons = []

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            buttons.append(QPushButton(title))
            button_layout.addWidget(buttons[index])
            self.stacklayout.addWidget(widget)
            # buttons[index].pressed.connect(lambda: self.activate_tab(index + 1))

        buttons[0].pressed.connect(lambda: self.activate_tab(1))
        buttons[1].pressed.connect(lambda: self.activate_tab(2))
        buttons[2].pressed.connect(lambda: self.activate_tab(3))
        buttons[3].pressed.connect(lambda: self.activate_tab(4))
        buttons[4].pressed.connect(lambda: self.activate_tab(5))
        
        #Menu główne:
        menu = self.menuBar()

        #FILE MENU :
        filemenu =menu.addMenu("&Plik")

        otworz = QAction("Otwórz",self)
        filemenu.addAction(otworz)
        otworz.triggered.connect(self.otworz)

        zapis = QAction("Zapisz",self)
        filemenu.addAction(zapis)
        zapis.setShortcut("Ctrl+S")
        #zapis.triggered.connect(self.zapisz(self.pawel))

        exit_app = QAction("Wyjście",self)
        filemenu.addAction(exit_app)
        exit_app.triggered.connect(lambda: exit())

        #EDIT MENU :
        editmenu = menu.addMenu("&Edycja")

        #PRZECHPDZENIE MIĘDZY SEKCJAMI MENU :
        sectionmenu = menu.addMenu("&Sekcja")
        section_buttons = []

        for index, (title, widget) in enumerate(zip(tab_titles, stacked_widgets)):
            section_buttons.append(QAction(title, self))
            sectionmenu.addAction(section_buttons[index])
            # section_buttons[index].triggered.connect(lambda: self.activate_tab(index))

        section_buttons[0].triggered.connect(lambda: self.activate_tab(1))
        section_buttons[1].triggered.connect(lambda: self.activate_tab(2))
        section_buttons[2].triggered.connect(lambda: self.activate_tab(3))
        section_buttons[3].triggered.connect(lambda: self.activate_tab(4))
        section_buttons[4].triggered.connect(lambda: self.activate_tab(5))

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def activate_tab(self, index):
        self.stacklayout.setCurrentIndex(index - 1)
    
    def update_animation_data(self):
        dane_pawel = self.pawel.data.dane
        dane_wiktor = self.wiktor.data.anim_data
        self.animation_view.update_animation_data({
            'dane_pawel': dane_pawel,
            'dane_wiktor': dane_wiktor,
        })

#OTWIERZANIE Z PLIKU JSON
    def otworz(self):
        print("otwieram")


#ZAPIS DO PLIKU JSON
    def zapisz(self,dane_pawel):

        data = "{\n\"dane:\" [\n"
        for i in range(0, 14):
            data += "     {\n"

            data += "        \"dane_id\": " + str(i) + ",\n"
            data += "        \"wartosc_dane\": " + str(dane_pawel.data.dane[i])

            data += "\n     }\n"
        data += "\n}"

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter('JSON Files (*.json)')

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]

            try:
                with open(file_path, 'w') as file:
                    json.dump({'data': data}, file)
                QMessageBox.information(self, 'File Saved', 'Data saved to JSON file successfully.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred while saving the file: {str(e)}')
