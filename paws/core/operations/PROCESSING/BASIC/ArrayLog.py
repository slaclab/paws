import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

class ArrayLog(Operation):
    """
    Take the base-10 logarithm of any array. 
    Any elements with non-positive values are removed. 
    """

    def __init__(self):
        input_names = ['x']
        output_names = ['logx']
        super(ArrayLog, self).__init__(input_names, output_names)
        self.input_doc['x'] = 'any array'
        self.input_doc['logx'] = 'array of log(x), same size as x, non-positive values replaced with np.nan'
        self.input_src['x'] = opmod.wf_input
        self.input_src['logx'] = opmod.wf_input
        self.input_type['x'] = opmod.ref_type
        self.input_type['logx'] = opmod.ref_type

    def run(self):
        x = self.inputs['x']
        # good_vals = elements for which both x and y have defined logarithm
        idx_ok = ((x > 0) & (~np.isnan(x)))
        logx = np.zeros(x.shape)
        logx[idx_ok] = np.log10(x[idx_ok])
        logx[np.invert(idx_ok)] = np.nan
        self.outputs['logx'] = logx 


