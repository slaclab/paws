from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    T_set=None,
    T_ramp=None,
    delay_time=0)
outputs=OrderedDict(
    report=None)
        
class SetCryoCon(Operation):
    """Set the temperature of the CryoCon"""

    def __init__(self):
        super(SetCryoCon,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['T_set'] = 'Desired setpoint in degrees C' 
        self.input_doc['T_ramp'] = 'Desired temperature ramp in degrees C per minute' 
        self.input_doc['delay_time'] = 'Seconds to sleep after setting the cryocon' 
        self.output_doc['report'] = 'dict reporting details of final state' 

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        T_set = self.inputs['T_set'] 
        T_ramp = self.inputs['T_ramp'] 
        delay = self.inputs['delay_time']
        self.message_callback('enabling cryocon')
        cl.enable_cryocon()
        self.message_callback('setting cryocon to {}, at {} degC/minute'.format(T_set,T_ramp))
        cl.set_cryocon(T_set,T_ramp)
        if delay:
            self.message_callback('delaying {} seconds...'.format(delay))
            time.sleep(delay)
            # TODO: implement a control to ensure the setpoint
        val = cl.read_cryocon()
        rpt = dict(targets=[T_set],final_values=[val])
        self.outputs['report'] = rpt
        #self.outputs['flag'] = True
        #else:
        #    self.outputs['report'] = {'STATUS':bool(stat)}
        #    self.outputs['flag'] = False 

