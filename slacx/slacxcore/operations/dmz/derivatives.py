import numpy as np

from slacxop import Operation


class DiscreteFirstDerivative(Operation):
    """Take the discrete analogue of the first derivative."""

    def __init__(self):
        input_names = ['x', 'y']
        output_names = ['slope']
        super(DiscreteFirstDerivative, self).__init__(input_names, output_names)
        self.input_doc['x'] = ''
        self.input_doc['y'] = ''
        self.output_doc['slope'] = ''
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['slope'] = discrete_first_derivative(self.inputs['x'], self.inputs['y'])

def discrete_first_derivative(x, y):
    pass