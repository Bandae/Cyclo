import math
import copy

from ..utils.dict_utils import fetch_data_subset

class InputMechanismCalculator():
    def __init__(self):
        self.bearings = {}
        self.data = {
            # Napęd
            'nwe':[750, 'obr/min'],         # Prędkość obrotowa wejściowa
            'w0':[78.54, 'rad/s'],          # Prędkość kątowa wejściowa
            'Mwe': [26.67, 'Nm'],           # Moment wejściowy - moment skręcający
            # Zadane wymiary wału
            'L': [None, 'mm'],              # Całkowita długość wału czynnego
            'e': [3, 'mm'],                 # Mimośród
            'B': [17, 'mm'],                # Długość koła obiegowego
            'x': [5, 'mm'],                 # Odległość pomiędzy dwoma kołami obiegowymi
            'rw1': [99, 'mm'],              # Promień koła toczengo (koło obiegowe)
            # Współrzędne podpór i kół obiegowych
            'LA': [None, 'mm'],             # Wsp. podpory przesuwnej - A
            'LB': [None, 'mm'],             # Wsp. podpory stałej - B
            'n': [2, ''],                   # Liczba kół obiegowych
            'L1': [None, 'mm'],             # Wsp. pierwszego koła obiegowego
            'Lc': {},                       # Wsp. kolejnych kół obiegowych - domyślnie brak
            # Dobrany materiał i parametry
            'Materiał' : None,              # Materiał wału
            'xz': [None, ''],               # Współczynnik bezpieczeństwa
            'qdop': [None, 'rad/m'],        # Dopuszczalny jednostkowy kąt skręcenia wału
            'tetadop': [None, 'rad'],       # Dopuszczalny kąt ugięcia wału
            'fdop': [None, 'mm'],           # Dopuszczalna strzałka ugięcia wału
            # Siły pochodzące od kół obiegowych
            'Fwzx': [4444.44, 'N'],         # Wypadkowa siła międzyzębna działająca w osi x
            'Fwzy': [2799.16, 'N'],         # Wypadkowa siła międzyzębn działająca w osi y
            'Fwm': [5602.25, 'N'],          # Wypadkowa siła w mechanizmie wyjściowym
            # Reakcje podporowe i siły działające na wał
            'Ra':[None, 'N'],               # Reakcja w podporze nieruchomej
            'Rb':[None, 'N'],               # Reakcja w podporze ruchomej
            'F': [None, 'N'],               # Siła pochodząca od koła obiegowego
            'Fx': {},                       # Siła na kole obiegowym 1
            # Obliczone wymiary wału
            'dsc': [None, 'mm'],            # Średnica wału wejściowego - obliczona
            'dec': [None, 'mm'],            # Średnica mimośrodu - obliczona
            # Straty mocy w mechanizmie
            'P': [None, 'W'],
            # Łożyska
            'Bearings': {
              # Podpora A
              'support_A': {                         
                'data': None,               # Parametry łożyska
                'bearing_type': None,       # Rodzaj łożyska
                'rolling_elements': None,   # Elementy toczne
                'F': None,                  # Siła działająca na łożysko 
                'dip': [None, 'mm'],        # Średnica wewnętrzna łożyska - na podstawie zaprojektowanego wału
                'di': [None, 'mm'],         # Średnica wewnętrzna łożyska
                'do': [None, 'mm'],         # Średnica zewnętrzna łożyska
                'drc': [None, 'mm'],        # Średnica elementów tocznych - obliczona
                'Lh': [None, 'h'],          # Trwałość godzinowa
                'Lr': [None, 'obr'],        # Trwałość
                'C': [None, 'kN'],          # Nośność
                'fd': [None, ''],           # Współczynnik zależny od zmiennych obciążeń dynamicznych
                'ft': [None, ''],           # Współczynnik zależny od temperatury pracy łożyska
                'f': [None, 'm'],           # Współczynnik tarcia tocznego
                'P': [None, 'W'],           # Straty mocy           
              },
               # Podpora B
              'support_B': {                         
                'data': None,               # Parametry łożyska
                'bearing_type': None,       # Rodzaj łożyska
                'rolling_elements': None,   # Elementy toczne
                'F': None,                  # Siła działająca na łożysko
                'dip': [None, 'mm'],        # Średnica wewnętrzna łożyska - na podstawie zaprojektowanego wału
                'di': [None, 'mm'],         # Średnica wewnętrzna łożyska
                'do': [None, 'mm'],         # Średnica zewnętrzna łożyska
                'drc': [None, 'mm'],        # Średnica elementów tocznych - obliczona
                'Lh': [None, 'h'],          # Trwałość godzinowa
                'Lr': [None, 'obr'],        # Trwałość
                'C': [None, 'kN'],          # Nośność
                'fd': [None, ''],           # Współczynnik zależny od zmiennych obciążeń dynamicznych
                'ft': [None, ''],           # Współczynnik zależny od temperatury pracy łożyska
                'f': [None, 'm'],           # Współczynnik tarcia tocznego
                'P': [None, 'W'],           # Straty mocy           
              },
               # Miośrody pod koła cykloidalne
              'eccentrics': {                         
                'data': None,               # Parametry łożyska
                'bearing_type': None,       # Rodzaj łożyska
                'rolling_elements': None,   # Elementy toczne
                'F': None,                  # Siła działająca na łożysko
                'l': None,                  # Położenie łożyska na wale
                'di': [None, 'mm'],         # Średnica wewnętrzna łożyska
                'do': [None, 'mm'],         # Średnica zewnętrzna łożyska
                'dip': [None, 'mm'],        # Średnica wewnętrzna łożyska - na podstawie zaprojektowanego wału
                'drc': [None, 'mm'],        # Średnica elementów tocznych - obliczona
                'Lh': [None, 'h'],          # Trwałość godzinowa
                'Lr': [None, 'obr'],        # Trwałość
                'C': [None, 'kN'],          # Nośność
                'fd': [None, ''],           # Współczynnik zależny od zmiennych obciążeń dynamicznych
                'ft': [None, ''],           # Współczynnik zależny od temperatury pracy łożyska
                'f': [None, 'm'],           # Współczynnik tarcia tocznego
                'P': [None, 'W'],           # Straty mocy           
              }
            }
        }
        self._add_data_reference()

    def _add_data_reference(self):
        self.data['Bearings']['support_A']['F'] = self.data['Ra']
        self.data['Bearings']['support_B']['F'] = self.data['Rb']
        self.data['Bearings']['eccentrics']['F'] = self.data['F']

        self.data['Bearings']['support_A']['l'] = self.data['LA']
        self.data['Bearings']['support_B']['l'] = self.data['LB']
        self.data['Bearings']['eccentrics']['l'] = self.data['L1']

    def calculate_bearings_attributes(self):
        """
        Calculate bearings attributes.
        """
        for attributes in self.data['Bearings'].values():
            Dz = attributes['data']['d_out'][0]
            Dw = attributes['data']['d_in'][0]

            dw = 0.25 * (Dz - Dw)

            attributes['drc'][0] = dw
            attributes['di'][0] = Dw
            attributes['do'][0] = Dz
    
    def calculate_absolute_power_loss(self):
        """
        Calculate absolute power loss in current mechanism.
        """
        absolute_power_loss = 0
        for bearing_section_id, attributes in self.data['Bearings'].items():
            absolute_power_loss += attributes['P'][0]
        
        self.data['P'][0] = absolute_power_loss

    def get_bearings_attributes_limits(self, bearing_section_id):
        """
        Get attributes limits of given bearing.

        Args:
            bearing_section_id (str): Id of section that specifies the bearing location.
        Returns
            (tuple): tuple (float, float) of limits: 
        """
        return self.data['Bearings'][bearing_section_id]['dip'][0], self.data['Bearings'][bearing_section_id]['C'][0]

    def get_rollings_element_limits(self, bearing_section_id):
        """
        Set attributes limits of given bearing rolling elements.

        Args:
            bearing_section_id (str): Id of section that specifies the bearing location.
        Returns
            (float): limit 
        """
        return self.data['Bearings'][bearing_section_id]['drc'][0]

    def get_bearing_type(self, bearing_section_id):
        """
        Get type of rolling emenet for given bearing

        Args:
            bearing_section_id (str): Id of section that specifies the bearing location.
        Returns:
            (str): type of bearing
        """
        return self.data['Bearings'][bearing_section_id]['bearing_type']['name'][0]
        
    def get_bearing_attributes(self, bearing_section_id, bearing_data):
        """
        Extract and organize necessary bearing attributes from provided
        bearing data.

        Args:
            bearing_section_id (str): The location id of the bearing.
            bearing_data (dict): Bearing data.
        Returns:
            (dict): Bearing attributes.
        """
        if bearing_data:
            Dw = bearing_data['d_in'][0]
            B = bearing_data['b'][0]

            if bearing_section_id == 'eccentrics':
                e = self.data['e'][0]
                Dz = bearing_data['e'][0]
            else:
                e = 0
                Dz = bearing_data['d_out'][0]

            bearing_data = {'Dw': Dw, 'Dz': Dz, 'B': B, 'e': e}

        return {bearing_section_id: bearing_data}
        
    def get_data(self):
        """
        Get component data.
        """
        return self.data
    
    def set_initial_data(self):
        fwzx = self.data['Fwzx'][0]
        fwzy = self.data['Fwzy'][0]
        fwm = self.data['Fwm'][0]

        self.data['F'][0] = (fwzx**2 + (fwm - fwzy)**2)**0.5

        if len(self.data['Lc']) != self.data['n'][0]-1:
            self.data['Lc'] = {}

            for idx in range(self.data['n'][0]-1):
                self.data['Lc'][f'L{idx+2}'] = copy.deepcopy(self.data['L1'])

            self.data['Fx'] = {}

        for idx in range(self.data['n'][0]):
            self.data['Fx'][f'F{idx+1}'] = copy.deepcopy(self.data['F'])
            self.data['Fx'][f'F{idx+1}'][0] = self.data['F'][0] * (-1)**idx

    def set_data(self, data):
        """
        Set component data.
        """
        self.data.update(data)
        self._add_data_reference()
    
    def update_data(self, data):
        """
        Update component data.

        Args (dict): New data to update the component data with.
        """   
        fetch_data_subset(self.data, data)
        self._add_data_reference()
