from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation

from xrsdkit.tools.piftools import unpack_old_pif, make_pif 

inputs=OrderedDict(pif=None)
outputs=OrderedDict(pif=None)

class PIFRefactor(Operation):
    """Build a new PIF from an old PIF"""

    def __init__(self):
        super(PIFRefactor,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'old pif object'
        self.output_doc['pif'] = 'new pif object'

    def run(self):
        p = self.inputs['pif']
        expt_id, t_utc, q_I, T_C, feats, pops, params, rpt = unpack_old_pif(p)

        pops = OrderedDict()
        import pdb; pdb.set_trace()

        csys = saxs_piftools.make_pif(pops)
        self.outputs['pif'] = csys

