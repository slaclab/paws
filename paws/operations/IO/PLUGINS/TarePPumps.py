from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(ppump_controllers=None)
outputs=OrderedDict()
        
class TarePPumps(Operation):
    """Tare an array of P-pump controllers."""

    def __init__(self):
        super(TarePPumps,self).__init__(inputs,outputs)
        self.input_doc['ppump_controllers'] = 'list of MitosPPumpController plugins'

    def run(self):
        ppcs = self.inputs['ppump_controllers'] 
        for ipp,ppc in enumerate(ppcs):
            ppc.tare()

