from collections import OrderedDict

import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

inputs = OrderedDict(x=None,y=None)
outputs = OrderedDict(x_y=None)

class Zip(Operation):
    """Zip two 1d arrays together."""

    def __init__(self):
        super(Zip, self).__init__(inputs, outputs)
        self.input_doc['x'] = '1d array'
        self.input_doc['y'] = '1d array, same size as x'
        self.output_doc['x_y'] = 'n x 2 array containing x and y'

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        x_y = np.array(zip(x, y))
        self.outputs['x_y'] = x_y

