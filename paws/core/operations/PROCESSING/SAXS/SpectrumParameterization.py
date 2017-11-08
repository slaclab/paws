from collections import OrderedDict

import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_fit 

inputs = OrderedDict(q_I=None,flags=None,fixed_params=[],fixed_param_values=[])
outputs = OrderedDict(params=None,q_I_guess=None)

class SpectrumParameterization(Operation):
    """Determine approximate parameterization for a SAXS spectrum.

    Any preprocessing (background subtraction, smoothing, 
    and any other corrections or cleaning)
    should be performed beforehand. 
    The algorithm for guessing parameters
    for the size distributions of spherical nanoparticles 
    was developed and originally contributed by Amanda Fournier.    
    """

    def __init__(self):
        super(SpectrumParameterization, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array '\
            'of wave vectors(1/Angstrom) and intensities (counts)'
        self.input_doc['flags'] = 'dict of population flags, similar to the output '\
            'of saxskit.saxs_classify.SaxsClassifier.classify()'
        self.input_doc['fixed_params'] = 'list of strings indicating '\
            'which parameters should be fixed to specified values- '\
            'these correspond one-to-one with fixed_param_values.'
        self.input_doc['fixed_param_values'] = 'list of values '\
            'to which the corresponding fixed_params will be set.'
        self.output_doc['params'] = 'dict of scattering equation parameters, '\
            'similar to the input of saxskit.saxs_fit.compute_saxs()'
        self.output_doc['q_I_guess'] = 'n-by-2 array of q and the intensity spectrum '\
            'corresponding to the returned scattering equation parameters'
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item

    def run(self):
        q_I = self.inputs['q_I']
        f = self.inputs['flags'] 
        p = saxs_fit.parameterize_spectrum(q_I,f)
        q_I_guess = None
        if not f['bad_data']:
            I_guess = saxs_fit.compute_saxs(q_I[:,0],f,p)
            q_I_guess = np.array([q_I[:,0],I_guess]).T
        self.outputs['params'] = p
        self.outputs['q_I_guess'] = q_I_guess 




