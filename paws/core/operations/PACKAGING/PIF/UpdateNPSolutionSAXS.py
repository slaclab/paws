from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_classify,saxs_fit 

inputs=OrderedDict(
    pif=None,
    q_I=None,
    temperature=None,
    flags=None,
    params=None,
    report=None)
outputs=OrderedDict(pif=None)

class UpdateNPSolutionSAXS(Operation):
    """Update a nanoparticle solution SAXS record"""

    def __init__(self):
        super(UpdateNPSolutionSAXS,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'old pif object'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.input_doc['temperature'] = 'temperature in degrees C'
        self.input_doc['flags'] = 'dict of boolean flags indicating scatterer populations'
        self.input_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.input_doc['report'] = 'dict reporting fit objectives, etc. '
        self.output_doc['pif'] = 'updated pif object'
        self.input_type['pif'] = opmod.workflow_item

    def run(self):
        p = self.inputs['pif']
        q_I = self.inputs['q_I'] 
        temp = self.inputs['temperature'] 
        f = self.inputs['flags'] 
        par = self.inputs['params'] 
        r = self.inputs['report'] 
        self.outputs['pif'] = p
        self.outputs['temperature'] = temp
        self.outputs['flags'] = f
        self.outputs['params'] = par
        self.outputs['report'] = r



