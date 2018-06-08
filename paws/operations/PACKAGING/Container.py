from collections import OrderedDict

from ..Operation import Operation

inputs = OrderedDict(data=None)
outputs = OrderedDict()

class Container(Operation):
    """Operation for holding a piece of data for use by its parent Workflow"""

    def __init__(self):
        super(Container,self).__init__(inputs,outputs) 
        self.input_doc['data'] = 'an object to keep in the container'
        
    def run(self):
        pass 

