from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(cryocon=None)
outputs=OrderedDict()
        
class StopCryoCon(Operation):
    """Stop control of the CryoCon"""

    def __init__(self):
        super(StopCryoCon,self).__init__(inputs,outputs)
        self.input_doc['cryocon'] = 'A CryoConController Plugin'

    def run(self):
        self.inputs['cryocon'].stop_control()

