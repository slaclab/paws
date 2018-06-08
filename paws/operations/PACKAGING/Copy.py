from collections import OrderedDict
import copy

from ..Operation import Operation

inputs = OrderedDict(data=None)
outputs = OrderedDict(data=None)

class Copy(Operation):
    """Copies one input with copy.deepcopy."""

    def __init__(self):
        super(Copy,self).__init__(inputs,outputs) 
        self.input_doc['data'] = 'any object'
        self.output_doc['data'] = 'the result of copy.deepcopy() on input `data`'
        
    def run(self):
        self.outputs['data'] = copy.deepcopy(self.inputs['data'])

