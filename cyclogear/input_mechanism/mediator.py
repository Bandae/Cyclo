
from PySide2.QtCore import Signal, QObject

class Mediator(QObject):
    shaftDesigningFinished = Signal()
    updateComponentData = Signal(int, dict)

    selectMaterial = Signal()
    selectBearingType = Signal(str)
    selectBearing = Signal(str, dict)
    selectRollingElement = Signal(str, dict)

    bearingChanged = Signal(str, object)

    def emit_shaft_designing_finished(self):
        self.shaftDesigningFinished.emit()
    
    def update_component_data(self, tab_id: int, data: dict):
        self.updateComponentData.emit(tab_id, data)

    def select_material(self):
        self.selectMaterial.emit()
    
    def select_bearing_type(self, bearing_section_id: str):
        self.selectBearingType.emit(bearing_section_id)
    
    def select_bearing(self, bearing_section_id: str, data: dict):
        self.selectBearing.emit(bearing_section_id, data)

    def select_rolling_element(self, bearing_section_id: str, data: dict):
        self.selectRollingElement.emit(bearing_section_id, data)

    def update_bearing(self, bearing_section_id: str, bearing_data: object):
        self.bearingChanged.emit(bearing_section_id, bearing_data)
