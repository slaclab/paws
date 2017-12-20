import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(data_1=None,data_2=None)
outputs=OrderedDict(data_diff=None)

class Subtract(Operation):
    """Subtract one piece of data from another."""

    def __init__(self):
        super(Subtract,self).__init__(inputs,outputs)        
        self.input_doc['data_1'] = 'first piece of data, used as subtrahend'
        self.input_doc['data_2'] = 'second piece of data, used as minuend'
        self.output_doc['data_diff'] = 'the result of subtracting '\
            'data_1 from data_2, i.e. data_diff = data_2 - data_1'

    def run(self):
        self.outputs['data_diff'] = self.inputs['data_2'] - self.inputs['data_1']

