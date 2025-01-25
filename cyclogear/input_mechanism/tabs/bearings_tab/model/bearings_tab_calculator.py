import numpy as np

class BearingsTabCalculator():
    def init_data(self, component_data, inputs, outputs):
        self._component_data = component_data
        self._inputs = inputs
        self._outputs = outputs
    
    def calculate_bearing_load_capacity(self, bearing_section_id, data):
        """
        Calculate bearing load capacity.
        """
        nwe = self._component_data['nwe'][0]
        F = self._component_data['Bearings'][bearing_section_id]['F'][0]

        attributes = data['Bearings'][bearing_section_id]
    
        lh = attributes['Lh'][0]
        fd = attributes['fd'][0]
        ft = attributes['ft'][0]
        p = 1 / 3 if  attributes['bearing_type']['name'][0] == 'kulkowe' else 3 / 10

        l = 60 * lh * nwe / np.power(10, 6)
        c = np.abs(F) * np.power(l, p) * ft / fd / 1000 # [kN]

        return c