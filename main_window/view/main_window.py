from functools import partial

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QHBoxLayout, QStackedLayout, QVBoxLayout, QAction, QGridLayout, QDialog, QDialogButtonBox, QLabel

from animation.animation_view import AnimationView

from .base_data_widget import BaseDataWidget
from .error_widget import ErrorWidget

from config import APP_ICON, APP_NAME

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._init_ui()

    def _init_ui(self):
        # Set window title
        self.setWindowTitle(APP_NAME)

        # Set window icon
        main_icon = QIcon()
        main_icon.addFile(APP_ICON)
        self.setWindowIcon(main_icon)

        # Set window size
        self.setMinimumSize(1050,750)
        self.showMaximized()

        # Set main layout
        self.central_widget = QWidget()
        self.main_layout = QGridLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self._init_animation_section()
        self._init_data_section()
        self._init_menu_bar()
    
    def _init_animation_section(self):
        # Set animation layout
        self.animation_layout = QStackedLayout()
        self.main_layout.addLayout(self.animation_layout,0,1,1,6)
        
        # Set error widget
        self.error_box = ErrorWidget(self.central_widget)
        self.error_box.show()
        self.error_box.resetErrors()

        # Set base data widget
        self.base_data = BaseDataWidget(self.central_widget)
        
        # Set help button
        self.help_button = QPushButton(self.central_widget)
        self.help_button.setIcon(QIcon("icons//pomoc_zarys1.png"))
        self.help_button.setIconSize(QSize(140, 140))
        self.help_button.resize(150, 150)
        self.help_label = QLabel("Otwórz obrazek pomocniczy", self.help_button)
        self.help_label.move(10, 10)
        self.help_button.pressed.connect(self.helpClicked)

    def _init_data_section(self):
        # Set data layout
        data_layout = QVBoxLayout()
        self.main_layout.addLayout(data_layout,0,7,1,3)

        # Set button layout
        self.button_layout = QHBoxLayout()
        data_layout.addLayout(self.button_layout)

        # Set stacklayout
        self.stacklayout = QStackedLayout()
        data_layout.addLayout(self.stacklayout)

    def _init_menu_bar(self):
        # Set main menu
        menu = self.menuBar()

        # Set file menu
        filemenu = menu.addMenu("&Plik")

        self.otworz = QAction("Otwórz",self)
        filemenu.addAction(self.otworz)

        self.zapis = QAction("Zapisz",self)
        filemenu.addAction(self.zapis)
        self.zapis.setShortcut("Ctrl+S")

        self.zapis_jako = QAction("Zapisz jako",self)
        filemenu.addAction(self.zapis_jako)

        # Set export menu
        eksport_menu = menu.addMenu("&Eksport")

        self.raport = QAction("Generuj raport", self)
        eksport_menu.addAction(self.raport)

        self.eksport_csv = QAction("Eksport wykresów", self)
        eksport_menu.addAction(self.eksport_csv)

        self.eksport_dxf = QAction("Eksport do DXF", self)
        eksport_menu.addAction(self.eksport_dxf)

        # Set sections menu
        self.sectionmenu = menu.addMenu("&Sekcja")

    def set_tabs(self, tabs: QWidget):
        self.tabs = tabs

        # Workaround - info about tabs is still needed in main_window
        self.gear_tab = self.tabs['Zarys']

        # Set animation view 
        self.animation_view = AnimationView(self.central_widget, self.gear_tab.data.dane_all.copy())
        self.animation_layout.addWidget(self.animation_view)
        self.animation_view.lower()
        # self.animation_view.animacja.animation_tick.connect(self.onAnimationTick)

        # Set tabs in the stacklayout and their tittles into navigation buttons
        for index, (title, tab) in enumerate(self.tabs.items()):
            button = QPushButton(title)
            self.button_layout.addWidget(button)
            tab.setParent(self)
            self.stacklayout.addWidget(tab)
            button.pressed.connect(partial(self.activateTab, index))

        # Set tabs in the section menu
        for index, (title) in enumerate(self.tabs.keys()):
            button = QAction(title, self)
            self.sectionmenu.addAction(button)
            button.triggered.connect(partial(self.activateTab, index))    
    
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
        if choice == 0:
            event.ignore()
        elif choice == 1:
            self.animation_view.closeEvent(event)
            return super().closeEvent(event)
        if choice == 2:
            self.zapis.trigger()
            self.animation_view.closeEvent(event)
            return super().closeEvent(event)
        
    def activateTab(self, index):
        old_index = self.stacklayout.currentIndex()
        if old_index == 0 or old_index == 1:
            list(self.tabs.values())[old_index].data.recalculate()
        
        self.stacklayout.setCurrentIndex(index)
        self.help_button.show()
        if index == 0:
            self.help_button.setIcon(QIcon("icons//pomoc_zarys1.png"))
        elif index == 1:
            self.help_button.setIcon(QIcon("icons//pomoc_mechanizm_I.bmp"))
        else:
            self.help_button.hide()
    
    # def onAnimationTick(self, kat):
    #     self.pin_out_tab.data.recalculate(kat)
    
    def updateAnimationData(self, dane):
        self.animation_view.animation.updateData(dane)
