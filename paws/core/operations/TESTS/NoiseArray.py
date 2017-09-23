import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

class NoiseArray(Operation):
    """Creates and outputs a square array of noise"""

    def __init__(self):
        input_names = ['size']
        output_names = ['array']
        super(NoiseArray,self).__init__(input_names,output_names) 
        self.input_doc['size'] = 'dimension of output array'
        self.output_doc['array'] = 'an array of noise'
        self.inputs['size'] = 100 
    
    def run(self):
        s = self.inputs['size']
        self.outputs['array'] = np.random.rand(s,s) 

