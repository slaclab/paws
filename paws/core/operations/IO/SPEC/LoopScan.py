from collections import OrderedDict
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    n_scan=1,
    exposure_time=10.,
    delay_time=10.,
    status_code=True)
outputs=OrderedDict(
    report=None,
    status_code=False)
        
class LoopScan(Operation):
    """Run a loop scan through a SpecInfoClient"""

    def __init__(self):
        super(LoopScan,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['exposure_time'] = 'The exposure time in seconds' 
        self.output_doc['response'] = 'Status report from SpecInfoServer'

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        n_scan = self.inputs['n_scan'] 
        t_exp = self.inputs['exposure_time'] 
        t_delay = self.inputs['delay_time'] 
        stat = self.inputs['status_code']
        if stat:
            resp = cl.run_loopscan(n_scan,t_exp,t_delay)
            self.outputs['report'] = resp
            self.outputs['status_code'] = bool(resp['status_code'])
        else:
            self.outputs['report'] = {'STATUS':bool(stat)}
            self.outputs['status_code'] = False 



