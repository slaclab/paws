from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    T_ramp=None,
    T_set=None,
    delay_time=None,
    flag=True)
outputs=OrderedDict(
    report=None,
    flag=False)
        
class SetCryoCon(Operation):
    """Set the temperature of the CryoCon"""

    def __init__(self):
        super(SetCryoCon,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['T_ramp'] = 'Desired temperature ramp in degrees C per minute' 
        self.input_doc['T_set'] = 'Desired setpoint in degrees C' 
        self.input_doc['delay_time'] = 'seconds to wait after setting temperature' 
        self.input_doc['flag'] = 'boolean flag for whether or not to proceed' 
        self.output_doc['report'] = 'dict reporting details of final state' 
        self.output_doc['flag'] = 'boolean, positive if the Operation finished' 

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        delay = self.inputs['delay_time'] 
        T_ramp = self.inputs['T_ramp'] 
        T_set = self.inputs['T_set'] 
        stat = self.inputs['flag']
        if bool(stat):
            cl.enable_cryocon()
            cl.set_cryocon(T_set,T_ramp)
            if delay:
                self.message_callback('waiting {} seconds...'.format(delay))
                time.sleep(delay)
                # TODO: implement a control to ensure the setpoint
            val = cl.read_cryocon()
            rpt = dict(targets=[T_set],final_values=[val])
            self.outputs['report'] = rpt
            self.outputs['flag'] = True
        else:
            self.outputs['report'] = {'STATUS':bool(stat)}
            self.outputs['flag'] = False 

