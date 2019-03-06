from collections import OrderedDict

import numpy as np

from ..Operation import Operation

inputs = OrderedDict(size=100)
outputs = OrderedDict(array=None)

class NoiseArray(Operation):
    """Creates and outputs a square array of noise"""

    def __init__(self):
        super(NoiseArray,self).__init__(inputs,outputs) 
        self.input_doc['size'] = 'dimension of output array'
        self.output_doc['array'] = 'an array of noise'
    
    def run(self):
        s = self.inputs['size']
        self.outputs['array'] = np.random.rand(s,s) 
        return self.outputs

