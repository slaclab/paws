import numpy as np

from slacxop import Operation


class MovingAverage(Operation):
    """Add two objects."""

    def __init__(self):
        input_names = ['augend', 'addend']
        output_names = ['sum']
        super(MovingAverage, self).__init__(input_names, output_names)
        self.input_doc['augend'] = 'array or number'
        self.input_doc['addend'] = 'array or number for which addition with augend is defined'
        self.output_doc['sum'] = 'augend plus addend'
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['sum'] = self.inputs['augend'] + self.inputs['addend']


class SavitzkyGolay(Operation):
    """Add two objects."""

    def __init__(self):
        input_names = ['augend', 'addend']
        output_names = ['sum']
        super(SavitzkyGolay, self).__init__(input_names, output_names)
        self.input_doc['augend'] = 'array or number'
        self.input_doc['addend'] = 'array or number for which addition with augend is defined'
        self.output_doc['sum'] = 'augend plus addend'
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['sum'] = self.inputs['augend'] + self.inputs['addend']


class RectangularUnweightedSmooth(Operation):
    """Applies rectangular (moving average) smoothing filter to 1d data.

    No error estimate used."""

    def __init__(self):
        input_names = ['data', 'm']
        output_names = ['smoothdata']
        super(RectangularUnweightedSmooth, self).__init__(input_names, output_names)
        self.input_doc['data'] = '1d ndarray'
        self.input_doc['m'] = 'integer number of data points to average locally'
        self.output_doc['smoothdata'] = 'smoothed 1d ndarray'
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['sum'] = self.inputs['augend'] + self.inputs['addend']


