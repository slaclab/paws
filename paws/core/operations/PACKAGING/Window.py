from collections import OrderedDict

import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

inputs=OrderedDict(
    x_y=None,
    x_min=None,
    x_max=None)
outputs=OrderedDict(x_y_window=None)

class Window(Operation):
    """
    Window an n-by-2 array x_y 
    such that x is bounded by specified limits 
    """

    def __init__(self):
        super(Window,self).__init__(inputs,outputs)        
        self.input_doc['x_y'] = 'n-by-2 array of x and y values'
        self.input_doc['x_min'] = 'inclusive minimum x value of output'
        self.input_doc['x_max'] = 'inclusive maximum x value of output'
        self.output_doc['x_y_window'] = 'n-by-2 array with x, y pairs for x_min <= x <= x_max'
        self.input_datatype['x_min'] = 'float'
        self.input_datatype['x_max'] = 'float'

    def run(self):
        x_y = self.inputs['x_y']
        x_min = self.inputs['x_min']
        x_max = self.inputs['x_max']
        idx_keep = ((x_y[:,0] >= x_min) & (x_y[:,0] <= x_max))
        self.outputs['x_y_window'] = x_y[idx_keep,:] 

