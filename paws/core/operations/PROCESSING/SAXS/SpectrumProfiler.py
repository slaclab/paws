import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class SpectrumProfiler(Operation):
    """
    This operation profiles a SAXS spectrum (I(q) vs. q)
    to determine some characteristics of the sample.
    Based on some measures of the overall shape of the spectrum,
    the spectrum is tested for scattering from precursors 
    (approximated as small dilute monodisperse spheres),
    scattering from dilute nanoparticles of various form factors 
    (currently only spheres),
    diffraction peaks
    (Voigt-like profiles due to crystalline arrangements),
    or some combination of the three.
    TODO: document algorithm here.

    Output a return code
    and a dictionary of the results.

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
        self.input_doc['dI'] = 'optional- 1d array of intensity uncertainty values I(q)'
        self.output_doc['features'] = str('dict profiling the input spectrum. '
        + 'See the documentation of paws.core.tools.saxstools.profile_spectrum().')
        self.input_src['q'] = opmod.wf_input
        self.input_src['I'] = opmod.wf_input
        self.input_src['dI'] = opmod.no_input
        self.input_type['q'] = opmod.ref_type
        self.input_type['I'] = opmod.ref_type

    def run(self):
        q, I = self.inputs['q'], self.inputs['I']
        dI = self.inputs['dI']
        d_r = saxstools.profile_spectrum(q,I)
        self.outputs['features'] = d_r 

