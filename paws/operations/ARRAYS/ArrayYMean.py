from collections import OrderedDict

import numpy as np

from ..Operation import Operation

inputs = OrderedDict(x_y_arrays=[])
outputs = OrderedDict(x_ymean=None)

class ArrayYMean(Operation):
    """
    Average the second column of one or more n-by-2 arrays
    """

    def __init__(self):
        super(ArrayYMean, self).__init__(inputs,outputs)
        self.input_doc['x_y_arrays'] = 'list of n-by-2 arrays'
        self.output_doc['x_ymean'] = 'n-by-2 array of x and mean(y)'

    def run(self):
        x_y_arrays = self.inputs['x_y_arrays']
        x_ymean = None
        if len(x_y_arrays) > 0:
            x_ymean = np.zeros(x_y_arrays[0].shape)
            x_ymean[:,0] = x_y_arrays[0][:,0]
            x_ymean[:,1] = np.mean([xy[:,1] for xy in x_y_arrays],axis=0)
        self.outputs['x_ymean'] = x_ymean 
        return self.outputs

