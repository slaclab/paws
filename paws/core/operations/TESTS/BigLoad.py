import numpy as np

from ..operation import Operation

class BigLoad(Operation):
    """An Operation testing class, creates and outputs a big array of noise"""

    def __init__(self):
        input_names = []
        output_names = ['big_array']
        super(BigLoad,self).__init__(input_names,output_names) 
        self.output_doc['big_array'] = 'a big array of noise'
        
    def run(self):
        self.outputs['big_array'] = np.random.rand(10000,10000) 

