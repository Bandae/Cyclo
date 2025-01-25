from PySide2.QtWidgets import QDialog, QVBoxLayout
from PySide2.QtCore import Signal

from .ItemsList import ItemsList

class DbItemsWindow(QDialog):
    '''
    This class creates a window for
    displaying and selection of items from the database
    '''
    itemSelected = Signal(dict)
    def __init__(self, parent):
        super().__init__(parent)

        self.initUI()
        
    def initUI(self):
        '''
        Init GUI
        '''
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.setItemsList()

    def setItemsList(self):
        '''
        Set ItemsList - for listing database items
        '''
        self.itemsList = ItemsList(self)
        self.itemsList.itemSelected.connect(self.onItemSelected)

        self.mainLayout.addWidget(self.itemsList)

    def updateList(self, *args, **kwargs):
        '''
        Update list of items and adjust the window size to fit it properly
        '''
        self.itemsList.updateList(*args, **kwargs)
        # TO DO: There is problem with setting the size of the window to fit properly the ItemsList - find another way to do it. TEDIOUS TO DO!!!
        self.setMinimumWidth(max(self.itemsList.horizontalHeader().minimumSectionSize() * self.itemsList.dataModel.columnCount(), 150))
        self.resize(self.itemsList.horizontalHeader().maximumSectionSize() * self.itemsList.dataModel.columnCount(), self.sizeHint().height())
    
    def onItemSelected(self, data):
        '''
        Intercept the selection signal from ItmesList
        and close thi window wit return code = 1.

        Args:
            data (dict): selected item data
        '''
        self.itemSelected.emit(data)
        self.accept()
