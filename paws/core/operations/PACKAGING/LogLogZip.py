from collections import OrderedDict

import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

inputs=OrderedDict(x=None,y=None)
outputs=OrderedDict(logx_logy=None)

class LogLogZip(Operation):
    """
    Take the base-10 logarithm of two 1d arrays, then zip them together.
    Any elements with non-positive or nan values are removed. 
    """

    def __init__(self):
        super(LogLogZip, self).__init__(inputs, outputs)
        self.input_doc['x'] = '1d array'
        self.input_doc['y'] = '1d array, same size as x'
        self.output_doc['logx_logy'] = 'n x 2 array containing log(x) and log(y)'

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        # good_vals = elements for which both x and y have defined logarithm
        good_vals = ((x > 0) & (y > 0) & (~np.isnan(x)) & (~np.isnan(y)))
        xy = zip(np.log10(x[good_vals]), np.log10(y[good_vals]))
        self.outputs['logx_logy'] = np.array(xy)


