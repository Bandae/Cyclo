from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QPushButton

from config import RESOURCES_DIR_NAME, dependencies_path

class InputMechanism(QWidget):
    """
    GUI class for the Input Shaft component.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self._initUI()

        self.isShaftDesigned = False

    def _initUI(self):
        """
        Initialize the user interface.
        """
        # Set layouts 
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

        self.tabsSectionLayout = QVBoxLayout()
        self.tabsSectionLayout.setContentsMargins(0, 0, 0, 0)
        self.navigationButtonsLayout = QHBoxLayout()
        self.navigationButtonsLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addLayout(self.tabsSectionLayout)
        self.mainLayout.addLayout(self.navigationButtonsLayout)

        # Set content
        self._initTabWidget()
        self._initFunctionButtons()

    def _initTabWidget(self):
        '''
        Init widget holding and managing tabs.
        '''
        self._tabWidget = QTabWidget(self)
        font = QFont('Arial', 10)
        self._tabWidget.tabBar().setFont(font)

        self.tabsSectionLayout.addWidget(self._tabWidget)

    def _initFunctionButtons(self):
        '''
        Init previous tab button, next tab button and preview button.
        '''
        # Create button for moving to previous tab 
        self._previousTabButton = QPushButton(self)
        self._previousTabButton.setFixedSize(QSize(30, 30))
        self._previousTabButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//previous_icon.png')))
        self._previousTabButton.setToolTip('Poprzednia zakładka')
        self._previousTabButton.setIconSize(QSize(25, 18))
        self._previousTabButton.clicked.connect(self._openPreviousTab)

        # Create button for moving to next tab 
        self._nextTabButton = QPushButton(self)
        self._nextTabButton.setFixedSize(QSize(30, 30))
        self._nextTabButton.setIcon(QIcon(dependencies_path(f'{RESOURCES_DIR_NAME}//icons//buttons//next_icon.png')))
        self._nextTabButton.setToolTip('Następna zakładka')
        self._nextTabButton.setIconSize(QSize(25, 18))
        self._nextTabButton.clicked.connect(self._openNextTab)

        # Create button for opening the shaft preview
        self.previewButton = QPushButton('Podgląd', self)
        self.previewButton.setToolTip('Otwórz podgląd wału')
        self.previewButton.setFixedSize(QSize(100, 30))
        font = QFont('Arial', 12, QFont.Bold)
        self.previewButton.setFont(font)

        distance_between_buttons = 10
        self.navigationButtonsLayout.setSpacing(distance_between_buttons)

        self.navigationButtonsLayout.addStretch(1)
        self.navigationButtonsLayout.addWidget(self._previousTabButton)
        self.navigationButtonsLayout.addWidget(self.previewButton)
        self.navigationButtonsLayout.addWidget(self._nextTabButton)
        self.navigationButtonsLayout.addStretch(1)

    def _openNextTab(self):
        """
        Move to the next tab.
        """
        next_index = self._tabWidget.currentIndex() + 1

        if next_index < self._tabWidget.count():
            self._tabWidget.setTabEnabled(next_index, True)
            self._tabWidget.setCurrentIndex(next_index)
    
    def _openPreviousTab(self):
        """
        Move to the previous tab.
        """
        previous_index = self._tabWidget.currentIndex() - 1

        if previous_index >= 0:
            self._tabWidget.setCurrentIndex(previous_index)

    def _onTabChange(self, tab_index = 0):
        """
        Perform actions after a change of tabs.
        """
        # Perform actions uppon the tab activation
        self._tabWidget.currentWidget().onActivated()

        # Disable the next tab button if the current tab is the last one
        if tab_index == self._tabWidget.count() - 1:
            self._nextTabButton.setEnabled(False)

        # Toggle the visibility of the previous tab button
        if tab_index == 0:
            self._previousTabButton.setEnabled(False)
        else:
            self._previousTabButton.setEnabled(True)

    def initTabs(self, tabs, tabs_titles):
        """
        Initialize tabs in the main window.
        """
        for tab, title in zip(tabs, tabs_titles):
            self._tabWidget.addTab(tab, title)
            tab.setCallback(self.updateAccessToNextTabs)
        
        # Disable all tabs except the first one
        for i in range(1, self._tabWidget.count()):
            self._tabWidget.setTabEnabled(i, False)
        
        # Connect change of the tabs in the tab_widget to the _onTabChange method
        self._tabWidget.currentChanged.connect(self._onTabChange)

        # Check first tab after app initialization
        self._onTabChange()

    def updateAccessToNextTabs(self, enable_nextTabButton, disableNextTabs):
        """
        Check and update the state of the next tab button.
        """
        self.enablePreviewButton(enable_nextTabButton)

        if self.isShaftDesigned and enable_nextTabButton:
            self._nextTabButton.setEnabled(True)
        else:
            self._nextTabButton.setEnabled(False)

        if disableNextTabs:
            self.disableNextTabs()
    
    def enablePreviewButton(self, enable):
        """
        Toggle the preview button visibility.

        Args:
            enable (bool): Specifies whether the preview button should be enabled (True) or disabled (False).
        """
        if self._tabWidget.currentIndex() == 0:
            self.previewButton.setEnabled(enable)

    def disableNextTabs(self):
        """
        Disable all tabs following the current tab.
        """
        for i in range(self._tabWidget.currentIndex() + 1, self._tabWidget.count()):
            self._tabWidget.setTabEnabled(i, False)
    
    def handleShaftDesigningFinished(self):
        """
        This method is called when the shaft design is confirmed. It sets the
        first tab as current tab and updates the acces to next tabs.
        """
        self.isShaftDesigned = True
        self._tabWidget.setCurrentIndex(0)
        self.updateAccessToNextTabs(True, True)
