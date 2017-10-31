from collections import OrderedDict

from ..Operation import Operation

inputs = OrderedDict(data=None)
outputs = OrderedDict(data=None)

class Identity(Operation):
    """Operation that loads its one input into its one output"""

    def __init__(self):
        super(Identity,self).__init__(inputs,outputs) 
        self.input_doc['data'] = 'this can actually be anything'
        self.output_doc['data'] = 'this ends up being whatever the input was'
        
    def run(self):
        """Load self.inputs['data'] into self.outputs['data']"""
        self.outputs['data'] = self.inputs['data']

