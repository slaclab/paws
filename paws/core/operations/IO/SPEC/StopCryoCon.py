from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    flag=True)
outputs=OrderedDict(
    flag=False)
        
class StopCryoCon(Operation):
    """Stop control of the CryoCon"""

    def __init__(self):
        super(StopCryoCon,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['flag'] = 'boolean flag for whether or not to proceed' 
        self.output_doc['report'] = 'dict reporting details of final state' 
        self.output_doc['flag'] = 'boolean, positive if the Operation finished' 

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        f = self.inputs['flag']
        if bool(f):
            cl.stop_cryocon()
            self.outputs['flag'] = True
        else:
            self.outputs['flag'] = False 

