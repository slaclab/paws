from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxs_pif_tools

inputs=OrderedDict(pif=None)
outputs=OrderedDict(
    q_I=None,
    t_utc=None,
    temperature=None,
    flags=None,
    params=None,
    report=None)

class UnpackNPSolutionSAXS(Operation):
    """Unpack a nanoparticle solution SAXS record"""

    def __init__(self):
        super(UnpackNPSolutionSAXS,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'pif object to be unpacked'
        self.output_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.output_doc['t_utc'] = 'UTC time in seconds'
        self.output_doc['temperature'] = 'temperature in degrees C'
        self.output_doc['flags'] = 'dict of boolean flags indicating scatterer populations'
        self.output_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.output_doc['report'] = 'dict reporting fit objectives, etc. '
        self.input_type['pif'] = opmod.workflow_item

    def run(self):
        pp = self.inputs['pif']

        q_I, t_utc, T_C, flg, par, rpt = saxs_pif_tools.unpack_pif(pp)

        self.outputs['q_I'] = q_I 
        self.outputs['t_utc'] = t_utc 
        self.outputs['temperature'] = T_C 
        self.outputs['flags'] = flg
        self.outputs['params'] = par
        self.outputs['report'] = rpt

