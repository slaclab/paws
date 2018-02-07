from collections import OrderedDict
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    exposure_time=None)
outputs=OrderedDict(response=None)
        
class LoopScan(Operation):
    """Run a loop scan through a SpecInfoClient"""

    def __init__(self):
        super(LoopScan,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['exposure_time'] = 'The exposure time in seconds' 
        self.output_doc['response'] = 'Status report from SpecInfoServer'

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        t_exp = self.inputs['exposure_time'] 
        import pdb; pdb.set_trace()


