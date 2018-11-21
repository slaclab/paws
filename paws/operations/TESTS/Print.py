from collections import OrderedDict

from ..Operation import Operation

inputs = OrderedDict(data=None)
outputs = OrderedDict()

class Print(Operation):
    """Operation for printing data"""

    def __init__(self):
        super(Print,self).__init__(inputs,outputs) 
        self.input_doc['data'] = 'an object to print'
        
    def run(self):
        self.message_callback(self.inputs['data'])
        return self.outputs

