from PySide2.QtCore import Signal

from .ITrackedWidget import ITrackedWidget

class ITrackedTab(ITrackedWidget):
    """
    Tab widget that extends the ITrackedWidget abstract class:
    - implement methods that should be overriden (but do not have to) by subclasses
    - override parent class method to implement additional functionalities
    """
    updateStateSignal = Signal()
    allInputsProvided = Signal()

    def __init__(self, parent):
        super().__init__(parent)

    def _onStateChecked(self, all_filled, state_changed):
        """
        Override parent class method to perform additional tasks after state checking.

        Update the data.
        """
        if all_filled:
            self.allInputsProvided.emit()

        super()._onStateChecked(all_filled, state_changed)
    
    def onActivated(self):
        """
        Override parent class method to call additional methods uppon activation.
        """
        super().onActivated()

        self.updateStateSignal.emit()
