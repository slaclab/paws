import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

class LogY(Operation):
    """
    Take the base-10 logarithm of the second column
    of a n-by-2 array.
    """

    def __init__(self):
        input_names = ['x_y']
        output_names = ['x_logy']
        super(LogY, self).__init__(input_names, output_names)
        self.input_doc['x_y'] = 'n-by-2 array of x and y values'
        self.output_doc['x_logy'] = 'n-by-2 array of x and log(y) values'
        self.input_type['x_y'] = opmod.workflow_item

    def run(self):
        x_y = self.inputs['x_y']
        if x_y is None:
            return
        # good_vals = elements for which y has defined logarithm
        idx_ok = ((x_y[:,1] > 0) & (~np.isnan(x_y[:,1])))
        x_logy = np.zeros(x_y.shape)
        x_logy[idx_ok,1] = np.log10(x_y[idx_ok,1])
        x_logy[np.invert(idx_ok),1] = np.nan
        x_logy[:,0] = x_y[:,0]
        self.outputs['x_logy'] = x_logy 


