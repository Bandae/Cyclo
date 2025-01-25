from abc import ABCMeta, abstractmethod

from PySide2.QtCore import QEvent
from PySide2.QtWidgets import QWidget

from .Input import Input
from .Output import Output

from .DataButton import DataButton

class ABCQWidgetMeta(ABCMeta, type(QWidget)):
    pass

class ITrackedWidget(QWidget, metaclass=ABCQWidgetMeta):
    """
    Widget that tracks its status.

    It provides a reusable interface for checking if all the inputs are provided and/or changed.
    """
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self._parent = parent

        if callback:
            self._callback = callback

    def _connectSignalsAndSlots(self):
        """
        Connect signals from every tracket input, output and item
        to method that checks the state.
        """
        for input in self._inputsToProvide:
            input.inputConfirmedSignal.connect(self._checkState)

        for output in self._outputsToProvide:
            output.textChanged.connect(self._checkState)

        for item in self._itemsToSelect:
            item.dataChangedSignal.connect(self._checkState)
    
    def _disconnectSignalsAndSlots(self):
        """
        Disconnect signals from every tracket input, output and item
        from method that checks the state.

        If the objects does not exist or their signals are not connected,
        do nothing, else disconnect the signals.
        """
        try:
            for input in self._inputsToProvide:
                input.inputConfirmedSignal.disconnect(self._checkState)

            for output in self._outputsToProvide:
                output.textChanged.disconnect(self._checkState)

            for item in self._itemsToSelect:
                item.dataChangedSignal.disconnect(self._checkState)
        except (TypeError, AttributeError, RuntimeError):
            pass

    def _setupStateTracking(self):
        """
        Set up inputs tracking.

        Connect inputConfirmedSignal and dataChangedSignal signals of custom Input and DataButton 
        widgets to the _checkState method.
        """
        self._disconnectSignalsAndSlots()

        self._inputsToProvide = self.findChildren(Input)
        self._outputsToProvide = self.findChildren(Output)
        self._itemsToSelect = self.findChildren(DataButton)

        self._connectSignalsAndSlots()

        self._original_state = self._getState()

    def _getState(self):
        """
        Retrieve the current state of all inputs in the widget.

        Returns:
            list : A list of values that the tracked inputs, outputs and items ale holding.
        """
        inputs_states = [input.value() for input in self._inputsToProvide]
        inputs_states += [output.value() for output in self._outputsToProvide]
        inputs_states += [item.id() for item in self._itemsToSelect]

        return inputs_states

    def _checkState(self):
        """
        Check the current state of subjects and invoke the callback function with appropriate arguments.

        This function is called whenever an input is changed. It checks the state of inputs in the
        widget, and calls the callback function.
        """
        all_provided, state_changed = self.checkStatus()

        self._onStateChecked(all_provided, state_changed)

    def _onStateChecked(self, all_provided, state_changed):
        """
        Perform tasks after state checking.

        Call the callback function with widget status attributes.

        Args:
            all_provided (bool): Are all inputs provided?
            state_changed (bool): Were the inputs changed?
        """
        self._callback(all_provided, state_changed)

    def checkStatus(self):
        """
        Check status of all tracked subjects.

        Returns:
            all_provided (bool): Are all inputs provided?
            state_changed (bool): Were the inputs changed?
        """
        state_changed = False
        current_state = self._getState()

        # Check if all inputs were provided
        all_provided = all(current_state)

        state_changed = current_state != self._original_state

        self._original_state = current_state
        return all_provided, state_changed
    
    def trackState(self, track):
        if track:
            self._disconnectSignalsAndSlots()
            self._connectSignalsAndSlots()
            self._original_state = self._getState()
        else:
            self._disconnectSignalsAndSlots()
        
        tracked_children = self.findChildren(ITrackedWidget)
        for tracked_child in tracked_children:
            tracked_child.trackState(track)

    def setCallback(self, callback):
        """
        Set callback

        Args:
            callback (callable): Function that should be called after state checking.
        """
        self._callback = callback

    @abstractmethod
    def initUI(self):
        """
        Initialize the user interface for the widget. Must be overridden in subclasses.
        """
        self._setupStateTracking()

    def onActivated(self):
        """
        Call appropriate methods time when the widget becomes visible.
        """
        for trackedWidget in self.findChildren(ITrackedWidget): trackedWidget.onActivated()
        self._checkState()
