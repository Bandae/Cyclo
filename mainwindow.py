from PySide6.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QPushButton, QWidget, QHBoxLayout, QStackedLayout, QVBoxLayout
from PySide6.QtGui import QIcon, QAction
from main_view import Animation_View
from pawel import Tab_Pawel
from wiktor import Tab_Wiktor
from milosz import Tab_Milosz
from kamil import Tab_Kamil
from eksportdanych import Eksport_Danych
import json
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

        self.pawel = Tab_Pawel(self)
        self.pawel.anim_data_updated.connect(self.update_animation_data)

        self.wiktor = Tab_Wiktor(self)
        self.wiktor.data.anim_data_updated.connect(self.update_animation_data)

        kamil = Tab_Kamil(self)
        milosz = Tab_Milosz(self)
        eksport = Eksport_Danych(self)

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
        self.stacked_widgets = [self.pawel, self.wiktor, milosz, kamil, eksport]
        buttons = []

        for index, (title, widget) in enumerate(zip(tab_titles, self.stacked_widgets)):
            buttons.append(QPushButton(title))
            button_layout.addWidget(buttons[index])
            self.stacklayout.addWidget(widget)
            buttons[index].pressed.connect(partial(self.activate_tab, index))
        
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

        for index, (title, widget) in enumerate(zip(tab_titles, self.stacked_widgets)):
            section_buttons.append(QAction(title, self))
            sectionmenu.addAction(section_buttons[index])
            section_buttons[index].triggered.connect(partial(self.activate_tab, index))

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def activate_tab(self, index):
        previous = self.stacklayout.currentIndex()
        new_data = self.stacked_widgets[previous].send_data()
        for i, tab_widget in enumerate(self.stacked_widgets):
            if i != previous:
                tab_widget.receive_data(new_data)

        self.stacklayout.setCurrentIndex(index)
    
    def update_animation_data(self, dane):
        self.animation_view.update_animation_data({
            'pawel': dane.get("pawel"),
            'wiktor': dane.get("wiktor"),
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
