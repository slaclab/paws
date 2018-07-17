from collections import OrderedDict
import copy

import numpy as np

from ..Operation import Operation

inputs=OrderedDict(
    x_y=None,
    x_value=None)
outputs=OrderedDict(
    nearest_y=None)

class NearestYValue(Operation):
    """Given an `x-value`, return the nearest y-value from n-by-2 array `x_y`"""

    def __init__(self):
        super(NearestYValue,self).__init__(inputs,outputs)        
        self.input_doc['x_y'] = 'zip object containing x and y values'
        self.input_doc['x_value'] = 'x value to match against `x_y`'
        self.output_doc['nearest_y'] = 'y value whose x value is closest to `x_value`'
        self.input_datatype['x_value'] = float

    def run(self):
        x_y = self.inputs['x_y']
        data_list = list(copy.deepcopy(x_y))
        x_values = np.array([itm[0] for itm in data_list])
        x_val = self.inputs['x_value']
        idx_nearest = np.argmin(np.abs(x_values-x_val))
        self.outputs['nearest_y'] = data_list[idx_nearest][1] 

