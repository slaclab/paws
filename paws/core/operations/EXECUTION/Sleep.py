from collections import OrderedDict
import time

from ..Operation import Operation

inputs = OrderedDict(duration=None)
outputs = OrderedDict()

class Sleep(Operation):
    """Operation for delaying the Workflow."""

    def __init__(self):
        super(Sleep,self).__init__(inputs,outputs) 
        self.input_doc['duration'] = 'sleep duration in seconds'
        
    def run(self):
        time.sleep(self.inputs['duration']) 

