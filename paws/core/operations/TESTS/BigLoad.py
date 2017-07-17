import numpy as np

from .. import Operation as op
from ..Operation import Operation

class BigLoad(Operation):
    """An Operation testing class, creates and outputs a big array of noise"""

    def __init__(self):
        input_names = ['size']
        output_names = ['big_array']
        super(BigLoad,self).__init__(input_names,output_names) 
        self.input_doc['size'] = 'dimension of big array'
        self.output_doc['big_array'] = 'a big array of noise'
        self.input_src['size'] = op.text_input    
        self.input_type['size'] = op.int_type
        self.inputs['size'] = 10000 
    
    def run(self):
        s = self.inputs['size']
        self.outputs['big_array'] = np.random.rand(s,s) 

