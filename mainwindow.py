from PySide6.QtWidgets import QTabWidget, QMainWindow, QPushButton, QWidget, QHBoxLayout, QStackedLayout, QVBoxLayout
from PySide6.QtGui import QIcon, QAction
from kamil import Tab_Kamil
from milosz import Tab_Milosz
from wiktor import Tab_Wiktor
from pawel import Tab_Pawel
from main_view import Main_View
from eksportdanych import Eksport_Danych

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Przekładnia Cykolidalna")
        self.setMinimumSize(1050,750)
        self.showMaximized()

        #ustawienie ikonki :
        main_icon = QIcon()
        main_icon.addFile("icons//mainwindow_icon.png")
        self.setWindowIcon(main_icon)

        # stworzenie osobnych kart dla każdej czesci aplikacji :

        tabs = QTabWidget()
        tabs.setMovable(True)
        tabs.setTabPosition(QTabWidget.North)

        view = Main_View()
        self.pawel = Tab_Pawel()
        kamil = Tab_Kamil()
        wiktor = Tab_Wiktor()
        milosz = Tab_Milosz()
        eksport = Eksport_Danych()

        pagelayout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(self.stacklayout)

        btn1 = QPushButton("Widok Główny")
        btn1.pressed.connect(self.activate_tab_1)
        button_layout.addWidget(btn1)
        self.stacklayout.addWidget(view)

        btn2 = QPushButton("Przekładnia Cykloidalna")
        btn2.pressed.connect(self.activate_tab_2)
        button_layout.addWidget(btn2)
        self.stacklayout.addWidget(self.pawel)

        btn3 = QPushButton("Mechanizm Wyjsciowy I")
        btn3.pressed.connect(self.activate_tab_3)
        button_layout.addWidget(btn3)
        self.stacklayout.addWidget(wiktor)

        btn4 = QPushButton("Mechanizm Wyjsciowy II")
        btn4.pressed.connect(self.activate_tab_4)
        button_layout.addWidget(btn4)
        self.stacklayout.addWidget(milosz)

        btn5 = QPushButton("Mechanizm Wejsciowy")
        btn5.pressed.connect(self.activate_tab_5)
        button_layout.addWidget(btn5)
        self.stacklayout.addWidget(kamil)

        btn6 = QPushButton("Eksport danych")
        btn6.pressed.connect(self.activate_tab_6)
        button_layout.addWidget(btn6)
        self.stacklayout.addWidget(eksport)

        #Menu główne:

        menu = self.menuBar()

        #FILE MENU :

        filemanu =menu.addMenu("&Plik")

        #EDIT MENU :

        editmenu = menu.addMenu("&Edycja")

        #PRZECHPDZENIE MIĘDZY SEKCJAMI MENU :

        sectionmenu = menu.addMenu("&Sekcja")

        btn_1 = QAction("Widok Główny",self)
        sectionmenu.addAction(btn_1)
        btn_1.triggered.connect(self.activate_tab_1)

        btn_2 = QAction("Przekładnia Cykloidalna", self)
        sectionmenu.addAction(btn_2)
        btn_2.triggered.connect(self.activate_tab_2)

        btn_3 = QAction("Mechanizm Wyjsciowy I", self)
        sectionmenu.addAction(btn_3)
        btn_3.triggered.connect(self.activate_tab_3)

        btn_4 = QAction("Mechanizm Wyjsciowy II", self)
        sectionmenu.addAction(btn_4)
        btn_4.triggered.connect(self.activate_tab_4)

        btn_5 = QAction("Mechanizm Wejsciowy", self)
        sectionmenu.addAction(btn_5)
        btn_5.triggered.connect(self.activate_tab_5)

        btn_6 = QAction("Eksport danych", self)
        sectionmenu.addAction(btn_6)
        btn_6.triggered.connect(self.activate_tab_6)


        #Pasek z Narzędziami :
        ###


        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

        self.setCentralWidget(widget)

    def activate_tab_1(self):
        self.stacklayout.setCurrentIndex(0)

    def activate_tab_2(self):
        self.stacklayout.setCurrentIndex(1)

    def activate_tab_3(self):
        self.stacklayout.setCurrentIndex(2)

    def activate_tab_4(self):
        self.stacklayout.setCurrentIndex(3)

    def activate_tab_5(self):
        self.stacklayout.setCurrentIndex(4)

    def activate_tab_6(self):
        self.stacklayout.setCurrentIndex(5)