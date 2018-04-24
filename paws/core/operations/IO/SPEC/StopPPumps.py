from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(ppump_controllers=None)
outputs=OrderedDict()
        
class StopPPumps(Operation):
    """Set an array of MitosPPumpControllers to idle."""

    def __init__(self):
        super(StopPPumps,self).__init__(inputs,outputs)
        self.input_doc['ppump_controllers'] = 'list of MitosPPumpController plugins'

    def run(self):
        ppcs = self.inputs['ppump_controllers'] 
        for ipp,ppc in enumerate(ppcs):
            ppc.set_idle()

