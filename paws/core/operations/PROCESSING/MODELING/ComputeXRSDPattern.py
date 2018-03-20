from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_math

inputs = OrderedDict(
    q=None,
    populations=None,
    params=None)
outputs = OrderedDict(
    I=None,
    q_I=None)

class ComputeSAXS(Operation):
    """Compute a SAXS spectrum, given parameters."""

    def __init__(self):
        super(ComputeSAXS, self).__init__(inputs, outputs)
        self.input_doc['q'] = 'array of wave vectors (1/Angstrom)'
        self.input_doc['populations'] = 'dict that counts scatterer populations'
        self.input_doc['params'] = '(optional) dict of parameters '\
            'used as initial condition for fit optimization. '\
            'defaults are chosen if not provided.'
        self.output_doc['I'] = 'array of computed intensities'
        self.output_doc['q_I'] = 'n-by-2 array of q and I'

    def run(self):
        q = self.inputs['q']
        pops = self.inputs['populations']
        pars = self.inputs['params']

        all_pops = OrderedDict.fromkeys(saxs_math.population_keys)
        all_pops.update(pops)
        I = saxs_math.compute_saxs(q,all_pops,pars)        

        self.outputs['I'] = I 
        self.outputs['q_I'] = np.vstack([q,I]).T 

