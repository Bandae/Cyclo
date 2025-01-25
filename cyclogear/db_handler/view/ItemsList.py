from PySide2.QtWidgets import QTableView, QHeaderView, QAbstractItemView
from PySide2.QtGui import QTextDocument, QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt, Signal

class RichTextHeader(QHeaderView):
    '''
    This class implements a header that supports HTML text, so subscripts and superscripts can be
    properly displayed.
    '''
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(False)

    def paintSection(self, painter, rect, logicalIndex):
        """
        Custom painting function for rendering header sections in a QHeaderView.

        This method overrides the default header section painting behavior, allowing 
        for more advanced customization such as rendering HTML-formatted text in the headers.
        It uses a QTextDocument to draw rich text content within the specified header section.

        Args:
            painter (QPainter): The QPainter object used to perform the drawing operations.
            rect (QRect): The rectangle area that defines the boundaries of the header section.
            logicalIndex (int): The logical index of the header section, used to fetch the 
                                corresponding data from the model.
        """
        painter.save()
        painter.translate(rect.topLeft())

        # Create a QTextDocument to render HTML
        doc = QTextDocument(self)
        doc.setHtml(self.model().headerData(logicalIndex, self.orientation(), Qt.ItemDataRole.DisplayRole))
        doc.setTextWidth(rect.width())

        # Calculate the vertical offset to ensure text is centered properly
        text_height = doc.size().height()
        vertical_offset = (rect.height() - text_height) / 2 - 1

        # Translate painter to correct position
        painter.translate(0, vertical_offset)

        # Draw the text
        doc.drawContents(painter)

        painter.restore()

    def sizeHint(self):
        return super().sizeHint()

class ItemsList(QTableView):
    """
    A custom QTableView class for displaying a list of items with selectable rows, 
    custom headers, and hover/selection styles. This class allows for dynamic 
    updates of headers and data, and emits a signal when an item is selected.

    Attributes:
        itemSelected (Signal): Signal emitted when an item is selected, 
                                   providing the selected item as a dictionary.
        headers (list): The list of headers for the table.
        keys (list): The list of keys used for mapping data to dictionary form.
        data (list): The list of data rows to be displayed in the table.
        dataModel (QStandardItemModel): The model backing the table view.
    """
    itemSelected = Signal(dict)

    # Style sheets for header, selected item, hover, and vertical scrollbar
    headerStyle = """
    QHeaderView::section {
        background-color: transparent;
        border: 0px;
        padding: 3px;
        margin: 0px;
    }
    QHeaderView::section:hover {
        background-color: transparent;
        border: 0px;
    }
    """
    selectedItemStyle = """
    QTableView::item:selected {
        background-color: lightblue;
        color: black;
    }
    """
    hoverItemStyle = """
    QTableView::item:hover {
        background-color: lightgray;
    }
    """
    verticalScrollbarStyle = """
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
    """

    def __init__(self, parent):
        """
        Initializes the ItemsList class and sets up the table view with the specified styles, 
        headers, selection behavior, and scrollbar settings.

        Args:
            parent: The parent widget of this QTableView.
        """
        super().__init__(parent)
        
        self.headers = None
        self.keys = None
        self.data = None

        self.dataModel = QStandardItemModel()
        self.setModel(self.dataModel)

        self._initUI()

    def _initUI(self):
        """
        Initializes the user interface settings for the table.
        """
        # Enable hover effect
        self.setMouseTracking(True)

        # Set up style sheets
        self.setStyleSheet(self.headerStyle + self.selectedItemStyle)

        # Scrollbar settings
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.verticalScrollBar().setStyleSheet(self.verticalScrollbarStyle)

        # Headers settings
        self.verticalHeader().hide()
        self.setHorizontalHeader(RichTextHeader(Qt.Orientation.Horizontal, self))
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setMinimumSectionSize(100)
        self.horizontalHeader().setMaximumSectionSize(120)
        self.horizontalHeader().setHighlightSections(False)

        # Selection mode and behavior
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Connect the itemSelected signal to the custom slot
        self.selectionModel().selectionChanged.connect(self.onItemSelected)

    def updateList(self, headers: list, keys: list, data: list):
        """
        Updates the table with new headers and data.

        Args:
            headers (list): The list of column headers to display.
            keys (list): A list of keys corresponding to the headers, used when 
                         emitting the selected item signal.
            data (list): A list of data rows to populate the table.
        """
        if self.headers != headers:
            self.updateHeaders(headers, keys)
        
        if self.data != data:
            self.updateData(data)
    
    def updateHeaders(self, headers, keys):
        """
        Updates the table headers.

        Args:
            headers (list): The list of column headers to set.
            keys (list): The list of keys corresponding to each header.
        """
        self.headers = headers
        self.keys = keys

        # (Re)set headers
        self.dataModel.clear()
        self.dataModel.setHorizontalHeaderLabels(self.headers)
    
    def updateData(self, data):
        """
        Updates the table with new data.

        Args:
            data (list): A list of data rows, where each row is a list of cell values.
        """
        self.data = data

        # Clear data
        self.dataModel.removeRows(0, self.dataModel.rowCount())

        # Populate table with data
        for row in data:
            items = [QStandardItem(str(cell)) for cell in row]
            self.dataModel.appendRow(items)

        self.resizeColumnsToContents()

    def onItemSelected(self, selected, deselected):
        """
        Slot that handles item selection. When a row is selected, it constructs a dictionary 
        containing the keys and selected data and emits the itemSelected signal.

        Args:
            selected (QItemSelection): The currently selected items.
            deselected (QItemSelection): The previously selected items.
        """
        indexes = selected.indexes()

        if indexes:
            row = indexes[0].row()
            result_dict = {key: [value, ""] for key, value in zip(self.keys, self.data[row])}
            self.itemSelected.emit(result_dict)
