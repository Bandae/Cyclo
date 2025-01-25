from ..model.db_handler import DbHandler
from ..view.DbItemsWindow import DbItemsWindow

class DbController:
    '''
    This class fetches appriopiate items from database and displays them in a window, where
    desired item can be selected.
    '''
    def __init__(self, view: DbItemsWindow) -> None:
        self._items_view = view
        self.data = None
        self._items_view.itemSelected.connect(self.save_data)
        
        self._db_handler = DbHandler()  

    def show_bearings(self, *args, **kwargs):
        '''
        Fetch bearings data and display it in a window.

        Returns:
            (bool): result of the window execution.
        '''
        self._items_view.setWindowTitle('Łożyska')
        self._items_view.updateList(*self._db_handler.fetch_bearings(*args, **kwargs))
        return self._items_view.exec_()

    def show_bearing_types(self, *args, **kwargs):
        '''
        Fetch bearings types data and display it in a window.

        Returns:
            (bool): result of the window execution.
        '''
        self._items_view.setWindowTitle('Rodzaje łożysk')
        self._items_view.updateList(*self._db_handler.fetch_bearing_types(*args, **kwargs))
        return self._items_view.exec_()

    def show_rolling_elements(self, *args, **kwargs):
        '''
        Fetch bearings rolling elements data and display it in a window.

        Returns:
            (bool): result of the window execution.
        '''
        self._items_view.setWindowTitle('Elementy toczne')
        self._items_view.updateList(*self._db_handler.fetch_rolling_elements(*args, **kwargs))
        return self._items_view.exec_()

    def show_materials(self):
        '''
        Fetch materials data and display it in a window.

        Returns:
            (bool): result of the window execution.
        '''
        self._items_view.setWindowTitle('Materiały')
        self._items_view.updateList(*self._db_handler.fetch_materials())
        return self._items_view.exec_()

    def save_data(self, data):
        '''
        Save temporary data of selected item.

        Args:
            data (dict): selecte item attributes.
        '''
        self.data = data