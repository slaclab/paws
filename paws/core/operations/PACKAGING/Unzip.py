from collections import OrderedDict

import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

inputs = OrderedDict(x_y=None)
outputs = OrderedDict(x=None,y=None)

class Unzip(Operation):
    """Unzip an array of x,y data"""

    def __init__(self):
        super(Unzip, self).__init__(inputs, outputs)
        self.output_doc['x_y'] = 'list of 2-element x,y iterables'
        self.input_doc['x'] = 'x values'
        self.input_doc['y'] = 'y values'

    def run(self):
        x_y = self.inputs['x_y']
        x = [itm[0] for itm in x_y]
        y = [itm[1] for itm in x_y]
        self.outputs['x'] = x
        self.outputs['y'] = y

