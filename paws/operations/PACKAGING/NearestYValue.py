from collections import OrderedDict
import copy

import numpy as np

from ..Operation import Operation

inputs=OrderedDict(
    x=None,
    y=None,
    x_value=None)
outputs=OrderedDict(
    nearest_y=None)

class NearestYValue(Operation):
    """Given an `x-value`, select the value from `y` corresponding to the nearest x-value from `x`"""

    def __init__(self):
        super(NearestYValue,self).__init__(inputs,outputs)        
        self.input_doc['x'] = 'list of x values'
        self.input_doc['y'] = 'list of y values corresponding to `x`'
        self.input_doc['x_value'] = 'x value to compare against `x`'
        self.output_doc['nearest_y'] = '`y` value whose corresponding `x` is closest to `x_value`'
        self.input_datatype['x'] = list
        self.input_datatype['y'] = list
        self.input_datatype['x_value'] = float

    def run(self):
        x = self.inputs['x']
        xa = np.array(x)
        y = self.inputs['y']
        x_val = self.inputs['x_value']
        self.message_callback('input x value: {}'.format(x_val))
        idx_nearest = np.argmin(np.abs(xa-x_val))
        nearest_x = x[idx_nearest]
        nearest_y = y[idx_nearest]
        self.message_callback('nearest y value: {}, at x = {}'.format(nearest_y,nearest_x))
        self.outputs['nearest_y'] = nearest_y

