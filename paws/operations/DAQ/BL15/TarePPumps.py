from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(ppump_controllers={})
outputs=OrderedDict()
        
class TarePPumps(Operation):
    """Tare an array of P-pump controllers."""

    def __init__(self):
        super(TarePPumps,self).__init__(inputs,outputs)
        self.input_doc['ppump_controllers'] = 'dict of MitosPPumpController plugins'

    def run(self):
        ppcs = self.inputs['ppump_controllers'] 
        for ppc_name,ppc in ppcs.items():
            ppc.tare()

