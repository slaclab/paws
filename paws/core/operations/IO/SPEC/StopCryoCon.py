from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(spec_infoclient=None)
outputs=OrderedDict()
        
class StopCryoCon(Operation):
    """Stop control of the CryoCon"""

    def __init__(self):
        super(StopCryoCon,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.output_doc['report'] = 'dict reporting details of final state' 

    def run(self):
        self.inputs['spec_infoclient'].stop_cryocon()

