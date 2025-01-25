from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QFont, QIcon 
from PySide2.QtWidgets import (QHBoxLayout, QMainWindow, QSizePolicy, QSpacerItem, QPushButton,
                             QVBoxLayout, QWidget, QScrollArea)

from .chart.Chart import Chart
from .chart.Chart_Plotter import Chart_Plotter
from .chart.Chart_ShaftViewer import Chart_ShaftViewer

from .chart.widgets.CheckboxDropdown import CheckboxDropdown

from config import APP_NAME, APP_ICON

from config import RESOURCES_DIR_NAME, dependencies_path

class ShaftDesigner(QMainWindow):
    """
    A class representing chart and interface to design the shaft

    This class is responsible for communication between chart and
    other components of the application and also for implementing
    the GUI for interactive shaft design
    """
    def __init__(self, windowTitle):
        super().__init__()
        self._initUI(windowTitle)
    
    def _initUI(self, designedPartName):
        # Set window parameters
        self._windowTitle = APP_NAME + ' - ' + designedPartName
        self.setWindowTitle(self._windowTitle)
        self.setWindowIcon(QIcon(APP_ICON))

        self.resize(800, 500)

        # Set main layout
        self.mainWidget = QWidget(self)
        self.mainWidget.setContentsMargins(0, 0, 0, 0)
        self.mainWidget.setStyleSheet("""
        QWidget {
            background-color: #ffffff;
        }
        """)
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.mainLayout.setSpacing(0)
        self.setCentralWidget(self.mainWidget)

        self._initToolbar()

        # Set content layout
        self.contentLayout = QHBoxLayout()
        self.contentLayout.setSpacing(0)
        self.mainLayout.addLayout(self.contentLayout)

        # Init content widgets
        self._initSidebar()
        self._initChart()

        # Add buttons to the toolbar
        self._setToolbarButtons()

        # Set initial view
        self.sidebar.setVisible(False)
    
    def _initToolbar(self):
        # Create custom toolbar
        self.toolbar = QWidget(self)
        self.toolbarLayout = QHBoxLayout(self.toolbar)
        self.toolbar.setObjectName('toolbarWidget')
        self.toolbar.setStyleSheet("""
        QWidget#toolbarWidget {
            background-color: #ffffff;
        }
        """)
        self.toolbar.setFixedHeight(40)
        self.toolbarLayout.setContentsMargins(0, 0, 0, 0)
        self.toolbarLayout.setSpacing(5)
        self.mainLayout.addWidget(self.toolbar)

        # Create default style of toolbar buttons 
        self.toolbarButtonsStyle = """                         
            QPushButton {
                background-color: transparent;
                color: black;
                border: 1px solid transparent;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #66beb2;
                border: 1px solid #66beb2;
            }
            QPushButton:pressed {
                background-color: #51988e;
                border: 1px solid #51988e;
            }
            QPushButton:checked {
                background-color: #66beb2;
                border: 1px solid #66beb2;                     
            }
        """

    def _initSidebar(self):
        # Set container for sidebar content
        self.container = QWidget()
        self.container.setObjectName("containerWidget")
        self.container.setStyleSheet("""
        QWidget#containerWidget {
            background-color: #ffffff;
        }
        """)
        self.sidebarLayout = QVBoxLayout(self.container)

        # Set a scroll area for the sidebar
        self.sidebar = QScrollArea()
        self.sidebar.setStyleSheet("""
        QScrollArea {
            background-color: #ffffff;
            border: none;
        }
        QScrollBar:vertical {
            border: none;
            background: white;
            width: 13px;
            margin: 10px 0 10px 0;
        }
        QScrollBar::handle:vertical {
            background: #b5b5b5;
            min-height: 20px;
            max-height: 80px;
            border-radius: 4px;
            width: 8px;
            margin-right: 5px
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;  /* Removes the buttons */
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        """)
        self.sidebar.setWidgetResizable(True)
        self.sidebar.setWidget(self.container)
        self.sidebar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.sidebar.setFixedWidth(260)

        self.contentLayout.addWidget(self.sidebar)

    def _initChart(self):
        # Create chart
        self.chart = Chart()
        self.plotter = Chart_Plotter(self.chart)
        self.shaftViewer = Chart_ShaftViewer(self.chart)

        # Set the focus policy to accept focus and then set focus to the canvas
        self.chart.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.chart.setFocus()

        self.contentLayout.addWidget(self.chart)
    
    def _setToolbarButtons(self):
        # Set sidebar toggle button
        toggleSidebarButton = QPushButton(self)
        toggleSidebarButton.setCheckable(True)
        toggleSidebarButton.setStyleSheet(self.toolbarButtonsStyle)
        toggleSidebarButton.setFixedSize(QSize(30, 30))
        toggleSidebarButton.setIconSize(QSize(24, 24))
        toggleSidebarButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//show_menu_icon.png')))
        toggleSidebarButton.setToolTip('Otwórz/zamknij pasek boczny')
        toggleSidebarButton.clicked.connect(self.toggleSidebar)
        self.toolbarLayout.addWidget(toggleSidebarButton)

        # Set adjust view action
        fitToWindowButton = QPushButton(self)
        fitToWindowButton.setStyleSheet(self.toolbarButtonsStyle)
        fitToWindowButton.setFixedSize(QSize(30, 30))
        fitToWindowButton.setIconSize(QSize(24, 24))
        fitToWindowButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//fit_to_window_icon.png')))
        fitToWindowButton.setToolTip("Dopasuj widok")
        fitToWindowButton.clicked.connect(self.chart.reset_initial_view)
        self.toolbarLayout.addWidget(fitToWindowButton)

        # Set menu with plots to view
        self._plotsMenu = CheckboxDropdown()
        self._plotsMenu.setFixedSize(QSize(30, 30))
        self._plotsMenu.setIconSize(QSize(24, 24))
        self._plotsMenu.stateChanged.connect(self._updatePlots)
        self._plotsMenu.setIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//show_plots_icon.png'), 'Wyświetl wykresy momentów')
        self.toolbarLayout.addWidget(self._plotsMenu)

        # Set menu with plots to view
        self._minDiametersMenu = CheckboxDropdown()
        self._minDiametersMenu.setFixedSize(QSize(30, 30))
        self._minDiametersMenu.setIconSize(QSize(24, 24))
        self._minDiametersMenu.stateChanged.connect(self._updatePlots)
        self._minDiametersMenu.setIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//show_min_diameters_icon.png'), 'Wyświetl wykresy średnic minimalnych')
        self.toolbarLayout.addWidget(self._minDiametersMenu)

        # Set menu with dimensions to display
        self._dimensionsMenu = CheckboxDropdown()
        self._dimensionsMenu.setFixedSize(QSize(30, 30))
        self._dimensionsMenu.setIconSize(QSize(24, 24))
        self._dimensionsMenu.setIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//show_dimensions_icon.png'), 'Wyświetl wymiary')
        self._dimensionsMenu.addItem('dimensions', 'Wymiary wału', 'Wyświetl wymiary wału', self._toggleDimensions)
        self._dimensionsMenu.addItem('coordinates', 'Współrzędne wału', 'Wyświetl współrzędne wału', self._toggleCoordinates)
        self.toolbarLayout.addWidget(self._dimensionsMenu)
        
        # Set button for displaying bearings
        self._toggleBearingsPlotButton = QPushButton(self)
        self._toggleBearingsPlotButton.setStyleSheet(self.toolbarButtonsStyle)
        self._toggleBearingsPlotButton.setFixedSize(QSize(30, 30))
        self._toggleBearingsPlotButton.setIconSize(QSize(24, 24))
        self._toggleBearingsPlotButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//show_bearings_icon.png')))
        self._toggleBearingsPlotButton.setToolTip("Wyświetl łożyska")
        self._toggleBearingsPlotButton.setCheckable(True)
        self._toggleBearingsPlotButton.setEnabled(False)
        self._toggleBearingsPlotButton.clicked.connect(self._toggleBearings)
        self.toolbarLayout.addWidget(self._toggleBearingsPlotButton)

        # Set button for confirming shaft project:
        self.confirmDraftButton = QPushButton(self)
        self.confirmDraftButton.setStyleSheet("""                         
            QPushButton {
                background-color: #fba9a9;
                border: 1px solid #fba9a9;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f97f7f;
                border: 1px solid #f97f7f;
            }
            QPushButton:pressed {
                background-color: #f97171;
                border: 1px solid #f97171;
            }
        """)
        font = QFont('Arial', 10, QFont.Bold)
        self.confirmDraftButton.setFont(font)
        self.confirmDraftButton.setFixedSize(QSize(180, 30))
        self.confirmDraftButton.setIconSize(QSize(24, 24))
        self.confirmDraftButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//approve_icon.png')))
        self.confirmDraftButton.setToolTip("Zatwierdź projekt wału")
        self.confirmDraftButton.setText("Zatwierdź Projekt")
        self.confirmDraftButton.setEnabled(False)
        self.toolbarLayout.addWidget(self.confirmDraftButton)

        spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.toolbarLayout.addSpacerItem(spacer)

    def _toggleDimensions(self, isChecked):
        if isChecked:
            if self._toggleBearingsPlotButton.isChecked():
                self._toggleBearingsPlotButton.click()
            self.shaftViewer.draw_shaft_dimensions()
        else:
            self.shaftViewer.remove_shaft_dimensions()

    def _toggleCoordinates(self, isChecked):
        if isChecked:
            if self._toggleBearingsPlotButton.isChecked():
                self._toggleBearingsPlotButton.click()
            self.shaftViewer.draw_shaft_coordinates()
        else:
            self.shaftViewer.remove_shaft_coordinates()

    def _toggleBearings(self, isChecked):
        if isChecked:
            for id in self._dimensionsMenu.getCheckedItems():
                self._dimensionsMenu.checkItem(id, False)
            self.shaftViewer.draw_bearings()            
        else:
            self.shaftViewer.remove_bearings()

    def _updatePlots(self):
        selectedPlots = self._plotsMenu.getCheckedItems() + self._minDiametersMenu.getCheckedItems()
        self.plotter.set_selected_plots(selectedPlots)

    def setSidebarSections(self, sections):
        # Set contents of the sidebar
        for section in sections.values():
            self.sidebarLayout.addWidget(section)

        # Add a spacer item at the end of the sidebar layout - keeps the contents aligned to the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.sidebarLayout.addSpacerItem(spacer)

    def appendSectionToSidebar(self, section):
        # Add section before spacer
        self.sidebarLayout.insertWidget(self.sidebarLayout.count() - 1, section)

    def removeSectionFromSidebar(self, section):
        for index in range(self.sidebarLayout.count()):
            item = self.sidebarLayout.itemAt(index)
            if item.widget() == section:
                # Remove the widget from the layout
                self.sidebarLayout.takeAt(index)
                # Hide the widget
                section.hide()
                # Optionally delete the widget
                section.deleteLater()
                break

    def setDraftFinishedTitle(self, isFinished):
        if isFinished:
            self.setWindowTitle(self._windowTitle + ' (Projekt Zatwierdzony)')
        else:
            self.setWindowTitle(self._windowTitle)

    def toggleSidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def show(self):
        if self.isHidden():
            super().show()
        else:
            # Restore the window if it's minimized or in the back
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
            self.activateWindow()
            self.raise_()
