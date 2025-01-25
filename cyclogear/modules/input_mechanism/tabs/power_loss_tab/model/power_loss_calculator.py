import numpy as np

class PowerLossTabCalculator():
    def init_data(self, component_data, inputs, outputs):
        self._component_data = component_data
        self._inputs = inputs
        self._outputs = outputs

    def calculate_bearing_power_loss(self, bearing_section_id, data):
        """
        Calculate bearing load capacity.
        """
        w0 = self._component_data['w0'][0]
        e = self._component_data['e'][0] * 0.001
        rw1 = self._component_data['rw1'][0] * 0.001
        F = self._component_data['Bearings'][bearing_section_id]['F'][0]
        Dw = self._component_data['Bearings'][bearing_section_id]['data']['d_in'][0] * 0.001
        Dz = self._component_data['Bearings'][bearing_section_id]['data']['d_out'][0] * 0.001

        attributes = data['Bearings'][bearing_section_id]
        f = attributes['f'][0]
        dw = attributes['rolling_elements']['d'][0] * 0.001
            
        S = 0.15 * (Dz - Dw) if bearing_section_id == 'eccentrics' else dw / 2
        P = f * w0 * (1 + (Dw + 2 * S) / dw) * (1 + e / rw1) * 4 * np.abs(F) / np.pi

        return P