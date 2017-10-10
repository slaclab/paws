import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class SpectrumProfiler(Operation):
    """
    This operation profiles a SAXS spectrum (I(q) vs. q)
    by taking various scalar quantities from the data.

    Outputs a dictionary of the results.

    This Operation is somewhat robust for noisy data,
    but any preprocessing (background subtraction, smoothing, or other cleaning)
    should be performed beforehand. 
    """

    def __init__(self):
        input_names = ['q_I', 'dI']
        output_names = ['features']
        super(SpectrumProfiler, self).__init__(input_names, output_names)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.output_doc['features'] = 'dict profiling the input spectrum. '\
        'See the documentation of paws.core.tools.saxstools.profile_spectrum().'
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['dI'] = opmod.no_input

    def run(self):
        q_I = self.inputs['q_I']
        if q_I is None:
            return
        d_prof = saxstools.profile_spectrum(q_I)
        self.outputs['features'] = d_prof

