import numpy as np

from .. import Operation as op
from ..Operation import Operation

class LogLogZip(Operation):
    """
    Take the base-10 logarithm of two 1d arrays, then zip them together.
    Any elements with non-positive values are removed. 
    """

    def __init__(self):
        input_names = ['x', 'y']
        output_names = ['logx_logy']
        super(LogLogZip, self).__init__(input_names, output_names)
        self.input_doc['x'] = '1d array'
        self.input_doc['y'] = '1d array, same size as x'
        self.output_doc['logx_logy'] = 'n x 2 array containing log(x) and log(y)'
        self.input_src['x'] = op.wf_input
        self.input_src['y'] = op.wf_input
        self.input_type['x'] = op.ref_type
        self.input_type['y'] = op.ref_type

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        if (x.shape != y.shape):
            raise ValueError("x and y arrays must have the same shape")
        # good_vals = elements for which both x and y have defined logarithm
        good_vals = ((x > 0) & (y > 0) & (~np.isnan(x)) & (~np.isnan(y)))
        xy = zip(np.log10(x[good_vals]), np.log10(y[good_vals]))
        self.outputs['logx_logy'] = np.array(xy)


