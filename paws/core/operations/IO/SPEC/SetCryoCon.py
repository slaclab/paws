from collections import OrderedDict
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    T_set=None)
outputs=OrderedDict(response=None)
        
class SetCryoCon(Operation):
    """Set the temperature of the CryoCon"""

    def __init__(self):
        super(SetCryoCon,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['T_set'] = 'Desired setpoint in degrees C' 
        self.output_doc['response'] = 'Response from SpecInfoServer'

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        T_set = self.inputs['T_set'] 
        import pdb; pdb.set_trace()


