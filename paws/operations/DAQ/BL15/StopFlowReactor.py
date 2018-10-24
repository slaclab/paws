from collections import OrderedDict
import os
import time

from ...Operation import Operation

inputs=OrderedDict(flow_reactor=None)
outputs=OrderedDict()
        
class StopFlowReactor(Operation):
    """Safely stop all components of a FlowReactor Plugin."""

    def __init__(self):
        super(StopFlowReactor,self).__init__(inputs,outputs)
        self.input_doc['flow_reactor'] = 'A FlowReactor Plugin'

    def run(self):
        fr = self.inputs['flow_reactor']
        ppcs = fr.inputs['ppumps'] 
        if any(ppcs):
            for pp_nm,pp in ppcs.items():
                pp.set_idle()
        cryo = fr.inputs['cryocon']
        if cryo:
            cryo.stop_control()
        #fr.stop()

    
