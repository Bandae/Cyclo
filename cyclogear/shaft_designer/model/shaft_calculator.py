class ShaftCalculator:
    def __init__(self):
        self.shaft_sections = {}
        self.bearings = {}
        self.limits = {}

    def calculate_shaft_sections(self, shaft_subsection_attributes = None):
        # Save subsection attrbutes
        self._save_shaft_sections_attributes(shaft_subsection_attributes)

        # Prepare dict storing shaft subsections plots attributes
        self._shaft_dimensions = []

        # Calculate shaft sections plots attributes
        if 'Mimośrody' in self.shaft_sections:
            self._calculate_eccentricities_section()
        if 'Przed Mimośrodami' in self.shaft_sections:
            self._calculate_section_before_eccentricities()
        if 'Pomiędzy Mimośrodami' in self.shaft_sections:
            self._calculate_section_between_eccentricities()
        if 'Za Mimośrodami' in self.shaft_sections:
            self._calculate_section_after_eccentricities()
        
        return self._shaft_dimensions
    
    def _calculate_eccentricities_section(self):
        section = 'Mimośrody'
        for subsection_number, subsection_data in self.shaft_sections[section].items():
            length = subsection_data['l']
            diameter = subsection_data['d']
            position = self._shaft_attributes['Li'][subsection_number]
            self._shaft_attributes['Bx'][subsection_number] = length
            offset = self._shaft_attributes['e'] * (-1)**subsection_number

            start_z = position - length / 2
            start_y = - diameter / 2 + offset 

            self._shaft_dimensions.append({'start': (start_z, start_y), 'l': length, 'd': diameter, 'e': offset})

    def _calculate_section_between_eccentricities(self):
        # Draw the shaft section between the eccentrics
        section = 'Pomiędzy Mimośrodami'
        start_z = self._shaft_attributes['Li'][0] + self.shaft_sections['Mimośrody'][0]['l'] / 2

        for subsection_number, subsection_data in self.shaft_sections[section].items():
            length = subsection_data['l']
            diameter = subsection_data['d']
            start_y = -diameter / 2

            self._shaft_dimensions.append({'start': (start_z, start_y), 'l': length, 'd': diameter})

            start_z += length # Update start_z for the next subsection

    def _calculate_section_before_eccentricities(self):
        # Draw the shaft section before the first eccentric
        section = 'Przed Mimośrodami'

        start_z = self._shaft_attributes['Li'][0] - self.shaft_sections['Mimośrody'][0]['l'] / 2

        for subsection_number, subsection_data in self.shaft_sections[section].items():
            length = subsection_data['l']
            diameter = subsection_data['d']
            start_z -= length
            start_y = -diameter / 2

            self._shaft_dimensions.append({'start': (start_z, start_y), 'l': length, 'd': diameter})
        
    def _calculate_section_after_eccentricities(self):
        # Draw the shaft section after the second eccentric
        section = 'Za Mimośrodami'
        last_eccentric_number = max(list(self.shaft_sections['Mimośrody'].keys()))
        start_z = self._shaft_attributes['Li'][-1] + self.shaft_sections['Mimośrody'][last_eccentric_number]['l'] / 2

        for subsection_number, subsection_data in self.shaft_sections[section].items():
            length = subsection_data['l']
            diameter = subsection_data['d']
            start_y = -diameter / 2
            
            self._shaft_dimensions.append({'start': (start_z, start_y), 'l': length, 'd': diameter})
            
            start_z += length  # Update start_z for the next subsection
    
    def _check_if_plots_meet_limits(self):
        meets_limits = True

        for section_name, section in self.shaft_sections.items():
            for subsection_number, subsection in section.items():
                for attribute, value in subsection.items():
                    min = self.limits[section_name][subsection_number][attribute]['min']
                    max = self.limits[section_name][subsection_number][attribute]['max']
                    if min <= value <= max:
                        continue
                    else:
                        meets_limits = False
                        if value < min:
                                subsection[attribute] = min
                        elif value > max:
                                subsection[attribute] = max

        return meets_limits

    def _save_shaft_sections_attributes(self, attributes):
        if attributes:
            section_name = attributes[0]
            section_number = attributes[1]
            data = attributes[2]
            common_section_data = attributes[3]
            
            if section_name not in self.shaft_sections:
                self.shaft_sections[section_name] = {}
            
            self.shaft_sections[section_name][section_number] = data

            if isinstance(common_section_data, dict):
                for subsection_attributes in self.shaft_sections[section_name].values():
                    subsection_attributes.update(common_section_data)
    
    def _set_bearings_attributes(self, bearing_attributes):
        if bearing_attributes:
            # If the bearing_attributes are not empty, update self.bearings
            for bearing, attributes in bearing_attributes.items():
                if attributes is None:
                    # If the attributes are None, remove the bearing from self.bearings if it exists
                    if bearing in self.bearings:
                        del self.bearings[bearing]
                else:
                    # If the bearing does not exist in self.bearings, initialize it
                    if bearing not in self.bearings:
                        self.bearings[bearing] = {}
                    # Update the bearing with the new attributes
                    self.bearings[bearing] = attributes

    def remove_shaft_subsection(self, section_name, subsection_number):
        # Remove the subsection from shaft sections attributes
        if section_name in self.shaft_sections and subsection_number in self.shaft_sections[section_name]:
            del self.shaft_sections[section_name][subsection_number]

            # Adjust the numbering of the remaining subsections
            new_subsections = {}
            if len(self.shaft_sections[section_name]):
                for num, data in enumerate(self.shaft_sections[section_name].values()):
                    new_subsections[num] = data
                self.shaft_sections[section_name] = new_subsections
            else:
                del self.shaft_sections[section_name]
                
    def calculate_limits(self, current_subsections):
        ds = self._shaft_attributes['ds']
        de = self._shaft_attributes['de']
        B = self._shaft_attributes['B']
        x = self._shaft_attributes['x']
        LA = self._shaft_attributes['LA']
        LB = self._shaft_attributes['LB']
        Li = self._shaft_attributes['Li']
        L = self._shaft_attributes['L']
        Bx = self._shaft_attributes['Bx']
        # Set initial limits for eccentrics
        self.limits = {
            'Mimośrody': {
                idx: {
                    'd': {'min': de, 'max': 1000},
                    'l': {'min': B, 'max': 2 * min(position - LA if idx == 0 else x + B - 0.5 * Bx[idx-1], # max distance to left
                                                   LB - position if idx == len(Li)-1 else x + B - 0.5 * Bx[idx+1])} # max distance to right
                } for idx, position in enumerate(Li)
            } 
        }

        for section_name, section in current_subsections.items():
            for subsection_number, section in enumerate(section):
                lmin = 0
                dmin = ds
                dmax = 1000
                if subsection_number == 0:
                    self.limits[section_name] = {}
                    if section_name == 'Przed Mimośrodami':
                        lmax = max(Li[0] - 0.5 * Bx[0], 0)
                    if section_name == 'Pomiędzy Mimośrodami':
                        lmax = Li[1] - Li[0] - 0.5 * (Bx[0] + Bx[1])
                    if section_name == 'Za Mimośrodami':
                        lmax = max(L - Li[-1] - 0.5 * Bx[-1], 0)
                else:
                    previous_subsection = self.limits[section_name][subsection_number - 1]
                    lmax = max(previous_subsection['l']['max'] - self.shaft_sections[section_name][subsection_number - 1]['l'], 0)
                self.limits[section_name][subsection_number] = {'d': {'min': dmin, 'max': dmax}, 'l': {'min': lmin, 'max': lmax}}

        return self.limits

    def calculate_bearings(self, bearing_attributes={}):
        self._set_bearings_attributes(bearing_attributes)

        self.bearings_plots_attributes = {}

        for bearing, attributes in self.bearings.items():
            Dw = attributes['Dw']
            Dz = attributes['Dz']
            B = attributes['B']
            e = attributes['e']

            length = B
            diameter = (Dz - Dw) / 2
            if bearing == 'eccentrics':
                coordinates = self._shaft_attributes['Li']
                for idx, l in enumerate(coordinates):
                    offset = e * (-1)**idx
                    start_z = l - 0.5 * B
                    for position in range(2):
                        start_y = -0.5 * Dz + (0.5 * (Dw + Dz)) * position + offset
                        if bearing+f'{idx+1}' not in self.bearings_plots_attributes:
                             self.bearings_plots_attributes[bearing+f'{idx+1}'] = {}
                        self.bearings_plots_attributes[bearing+f'{idx+1}'][position] = {'start': (start_z, start_y), 'l': length, 'd': diameter}       
            else:
                if bearing == 'support_A':
                    l = self._shaft_attributes['LA']
                elif bearing == 'support_B':
                    l = self._shaft_attributes['LB']
                start_z = l - 0.5 * B
                for position in range(2):
                        start_y = -0.5 * Dz + (0.5 * (Dw + Dz)) * position
                        if bearing not in self.bearings_plots_attributes:
                            self.bearings_plots_attributes[bearing] = {}
                        self.bearings_plots_attributes[bearing][position] = {'start': (start_z, start_y), 'l': length, 'd': diameter}
            
        return self.bearings_plots_attributes

    def is_whole_shaft_designed(self):
        total_length = 0
    
        for step_dimensions in self._shaft_dimensions:
                length = step_dimensions['l']
                total_length += length
        
        return total_length == self._shaft_attributes['L']
    
    def get_sections_dimensions(self):
        return self.shaft_sections

    def get_shaft_attributes(self):
        shaft_steps = []
        for step_dimensions in self._shaft_dimensions:
                z = step_dimensions['start'][0]
                l = step_dimensions['l']
                d = step_dimensions['d']
                e = step_dimensions['e'] if 'e' in step_dimensions else 0

                shaft_steps.append({'z': z, 'l': l, 'd': d, 'e': e})
        
        shaft_steps.sort(key=lambda x: x['z'])
        
        return shaft_steps

    def set_data(self, shaft_attributes):
        self._shaft_attributes = shaft_attributes

    def save_data(self, data):
        LA = self._shaft_attributes['LA']
        LB = self._shaft_attributes['LB']
        L1 = self._shaft_attributes['Li'][0]
       
        support_places = [ [LA, None], [LB, None], [L1, None],]

        shaft_steps = self.get_shaft_attributes()
        for support in support_places:
            for step in shaft_steps:
                if step['z'] + step['l'] > support[0]:
                    support[1] = step['d']
                    break
        
        data['Bearings']['support_A']['dip'][0] = support_places[0][1]
        data['Bearings']['support_B']['dip'][0] = support_places[1][1]
        data['Bearings']['eccentrics']['dip'][0] = support_places[2][1]
