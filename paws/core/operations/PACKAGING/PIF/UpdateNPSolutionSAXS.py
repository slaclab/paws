from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxs_pif_tools

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
        self.input_doc['q_I'] = 'n-by-2 array of scattering vector q (1/Angstrom) and intensity (arb)'
        self.input_doc['temperature'] = 'temperature of sample in degrees C'
        self.input_doc['flags'] = 'dict of boolean flags indicating scatterer populations'
        self.input_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.input_doc['report'] = 'dict reporting fit objectives, etc. '
        self.output_doc['pif'] = 'updated pif object'

    def run(self):
        pp = self.inputs['pif']
        flg = self.inputs['flags'] 
        par = self.inputs['params'] 
        rpt = self.inputs['report'] 

        pnew = saxs_pif_tools.update_pif(pp,flg,par,rpt)

        self.outputs['pif'] = pnew

