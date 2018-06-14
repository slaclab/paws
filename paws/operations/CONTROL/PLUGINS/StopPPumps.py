from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(ppumps=None)
outputs=OrderedDict()
        
class StopPPumps(Operation):
    """Set an array of MitosPPumpControllers to idle."""

    def __init__(self):
        super(StopPPumps,self).__init__(inputs,outputs)
        self.input_doc['ppumps'] = 'dict of MitosPPumpController plugins'

    def run(self):
        ppcs = self.inputs['ppumps'] 
        for pp_nm,pp in ppcs.items():
            pp.set_idle()
            #ppc.set_flowrate(0)

