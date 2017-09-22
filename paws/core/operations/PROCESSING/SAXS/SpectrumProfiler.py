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
        input_names = ['q', 'I', 'dI']
        output_names = ['features']
        super(SpectrumProfiler, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array of wave vector values in 1/Angstrom units'
        self.input_doc['I'] = '1d array of intensity values I(q)'
        self.output_doc['features'] = 'dict profiling the input spectrum. '\
        'See the documentation of paws.core.tools.saxstools.profile_spectrum().'
        self.input_type['q'] = opmod.workflow_item
        self.input_type['I'] = opmod.workflow_item

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        if q is None or I is None:
            return
        d_r = saxstools.profile_spectrum(q,I)
        self.outputs['features'] = d_r 

