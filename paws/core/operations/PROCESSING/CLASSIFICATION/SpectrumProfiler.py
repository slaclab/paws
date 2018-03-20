import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_math 

inputs = OrderedDict(
    q_I=None,
    dI=None)
outputs = OrderedDict(
    features=None)

class SpectrumProfiler(Operation):
    """Profile a SAXS spectrum and return some numerical metrics.

    This operation profiles a SAXS spectrum (I(q) vs. q)
    by taking various scalar quantities from the data.
    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        super(SpectrumProfiler, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.output_doc['features'] = 'dict profiling the input spectrum. '\
        'See the documentation of saxskit.saxs_fit.profile_spectrum().'

    def run(self):
        q_I = self.inputs['q_I']
        d_prof = saxs_math.profile_spectrum(q_I)
        self.outputs['features'] = d_prof

