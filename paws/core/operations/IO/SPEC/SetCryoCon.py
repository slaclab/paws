from collections import OrderedDict
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    T_set=None,
    precision=0.01,
    status_code=True)
outputs=OrderedDict(
    report=None,
    status_code=False)
        
class SetCryoCon(Operation):
    """Set the temperature of the CryoCon"""

    def __init__(self):
        super(SetCryoCon,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['T_set'] = 'Desired setpoint in degrees C' 
        self.input_doc['precision'] = 'fractional precision for temperature' 
        self.input_doc['status_code'] = 'boolean flag for whether or not to proceed' 
        self.output_doc['report'] = 'dict reporting details of final state' 
        self.output_doc['status_code'] = 'boolean, positive iff the targets were achieved' 

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        T_set = self.inputs['T_set'] 
        prec = self.inputs['report'] 
        stat = self.inputs['status_code'] 
        if bool(stat):
            cl.set_cryocon(T_set)
            done = False
            while not done:
                val = cl.read_cryocon()
                if abs(val-T_set)/T_set < prec:
                    done = True
                # TODO:
                # delay, then check again
                # implement a maximum wait time
            rpt = dict(targets=[T_set],final_values=[val])
            self.outputs['report'] = rpt
            self.outputs['status_code'] = True
        else:
            self.outputs['report'] = {'STATUS':bool(stat)}
            self.outputs['status_code'] = False 



