class DriveShaftTabCalculator:
    def init_data(self, component_data, inputs, outputs, validated_inputs):
        self._component_data = component_data
        self._inputs = inputs
        self._outputs = outputs   
        self._validated_inputs = validated_inputs
    
    def _is_input_valid(self, input_name):
        """
        This function gets triggered when the user confirms the given input or at the limits 
        (re)initialization. It checks if the input is valid and depending on the result, takes actions.

        Args:
            input_name (str): Name of input which content is validated
        Returns:
            (bool): Value representing the validity of the input
        """
        input = self._inputs[input_name][0]
        value = input.value()
        if value is None:
            return False
        
        min_value, max_value = self.validated_inputs_limits[input_name]
        if min_value <= value <= max_value:
            self.validated_inputs_values[input_name] = value
            return True
        return False

    def _enable_next_input(self, input_name):
        """
        Enable the next input from validated inputs after the one which name is provided and if its value 
        is invalid, clear its text.

        Args:
            input_name (str): Name of input before the input to enable.
        """
        idx = self._validated_inputs.index(input_name)
        if idx < len(self._validated_inputs) - 1:
            next_input_name = self._validated_inputs[idx + 1]
            self._inputs[next_input_name][0].setEnabled(True)
            self._set_input_limits(next_input_name)
            if not self._is_input_valid(next_input_name):
                self._inputs[next_input_name][0].clear()
    
    def _clear_and_disable_subsequent_inputs(self, input_name):
        """
        Clear and disable all the validated inputs that come after the input which name is 
        provided.

        Args:
            input_name (str): name of the input after which perform the the disabling
        """
        idx = self._validated_inputs.index(input_name)
        for name in self._validated_inputs[idx + 1:]:
            self._inputs[name][0].setPlaceholderText('')
            self._inputs[name][0].clear()
            self._inputs[name][0].setDisabled(True)
        for position in self._inputs['Lc'].values():
                position[0].clear()

    def _set_input_limits(self, input_name):
        """
        Calculate, set and save the limits for the input which name was provided.

        Args:
            input_name (str): name of the input for which the limits are set
        """

        if input_name == 'L':
            min_value = self._component_data['x'][0] + 2 * self._component_data['B'][0]
            max_value = 1000
        elif input_name == 'LA':
            min_value = 0
            max_value = self.validated_inputs_values['L']
        elif input_name == 'LB':
            min_value = self.validated_inputs_values['LA'] + 2 * self._component_data['B'][0] + self._component_data['x'][0]
            max_value = self.validated_inputs_values['L']
        elif input_name == 'L1':
            min_value =  self.validated_inputs_values['LA'] + 0.5 * self._component_data['B'][0]
            max_value = self.validated_inputs_values['LB'] - 0.5 * self._component_data['B'][0] - (self._component_data['x'][0] + self._component_data['B'][0]) * (self._component_data['n'][0] - 1)
        
        self.validated_inputs_limits[input_name] = (round(min_value, 2), round(max_value, 2))
        self._inputs[input_name][0].setPlaceholderText(f"{min_value:.2f}-{max_value:.2f}")
    
    def setup_inputs_validation(self):
        """
        This function gets triggered when the user switches onto current ITrackedTab.
        It (re)initializes and applies the input limits of the validated_inputs.
        """
        self.validated_inputs_limits = {}
        self.validated_inputs_values = {}

        self._set_input_limits('L')
        for name in self._validated_inputs:
            if self._inputs[name][0].isEnabled():
                self.validate_input(self._inputs[name][0])

    def validate_input(self, input=None):
        """
        This function gets triggered when the user confirms the given input or at the limits 
        (re)initialization. It checks if the input is valid and depending on the result, takes actions.

        Args:
            input (Input): input which content is validated
        """
        input = self.sender() if input == None else input
        input_name = next((name for name, i in self._inputs.items() if i[0] == input), None)
        if self._is_input_valid(input_name):
            self._enable_next_input(input_name)
        else:
            self._inputs[input_name][0].clear()
            self._clear_and_disable_subsequent_inputs(input_name)

    def update_eccentrics_position(self):
        """
        This function gets triggered when the user changes the position
        of the first eccentric. It calculates and updates the positions
        of the following eccentrics.
        """
        L1 = self._inputs['L1'][0].value()
        if L1:
            for idx, position in enumerate(self._inputs['Lc'].values()):
                x = self._component_data['x'][0]
                B = self._component_data['B'][0]
                Lx =  L1 + (idx+1) * (x  + B)
                position[0].setValue(Lx)
        else:
            for position in self._inputs['Lc'].values():
                position[0].clear()
