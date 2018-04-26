from collections import OrderedDict

import numpy as np

from ...Operation import Operation

inputs = OrderedDict(x_y=None)
outputs = OrderedDict(x_logy=None)

class LogY(Operation):
    """
    Base-10 logarithm of second column of n-by-2 array.
    """

    def __init__(self):
        super(LogY, self).__init__(inputs,outputs)
        self.input_doc['x_y'] = 'n-by-2 array of x and y values'
        self.output_doc['x_logy'] = 'n-by-2 array of x and log_10(y) values'

    def run(self):
        x_y = np.array(self.inputs['x_y'])
        # good_vals = elements for which y has defined logarithm
        idx_ok = ((x_y[:,1] > 0) & (~np.isnan(x_y[:,1])))
        x_logy = np.zeros(x_y.shape)
        x_logy[idx_ok,1] = np.log10(x_y[idx_ok,1])
        x_logy[np.invert(idx_ok),1] = np.nan
        x_logy[:,0] = x_y[:,0]
        self.outputs['x_logy'] = x_logy 


