from PySide2.QtCore import Signal

from utils.widgets.PushButton import PushButton

class DataButton(PushButton):
    dataChangedSignal = Signal(object)

    def __init__(self, defaultText='', parent=None):
        super().__init__(defaultText, parent)
        self._data = None
        self._id = None
        self._defalultText = defaultText

        if defaultText:
            self.setText(defaultText)

    def _setID(self):
        self._id = str(next(iter(self._data.values()))[0])
        self.setText(self._id)

    def setData(self, data):
        if data:
            self._data = data
            self._setID()
            self.dataChangedSignal.emit(self._data)
    
    def clear(self):
        self._data = None
        self._id = None
        self.setText(self._defalultText)
        self.dataChangedSignal.emit(self._data)

    def id(self):
        return self._id

    def data(self):
        return self._data
