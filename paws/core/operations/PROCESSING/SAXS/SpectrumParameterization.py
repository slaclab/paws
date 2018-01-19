from __future__ import print_function
from collections import OrderedDict

import numpy as np
from scipy import interp
from scipy.optimize import minimize

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_fit, saxs_math 
from saxskit.saxs_regression import SaxsRegressor

inputs = OrderedDict(
    q_I=None,
    populations=None)
outputs = OrderedDict(
    params=None,
    q_I_guess=None)

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
        self.input_doc['populations'] = 'dict of populations, similar to the output '\
            'of saxskit.saxs_classify.SaxsClassifier.classify()'
        self.output_doc['params'] = 'dict of scattering equation parameters, '\
            'similar to the input of saxskit.saxs_fit.compute_saxs()'
        self.output_doc['q_I_guess'] = 'n-by-2 array of q and the intensity spectrum '\
            'corresponding to the returned scattering equation parameters'

    def run(self):
        q_I = self.inputs['q_I']
        pops = OrderedDict.fromkeys(saxs_math.population_keys)
        pops.update(self.inputs['populations'])
        sxr = SaxsRegressor()
        feats = saxs_math.profile_spectrum(q_I)
        params = sxr.predict_params(pops,feats,q_I)
        q_I_guess = None
        if not bool(pops['unidentified']):
            I_guess = saxs_math.compute_saxs(q_I[:,0],pops,params)
            q_I_guess = np.array([q_I[:,0],I_guess]).T

        self.outputs['params'] = params 
        self.outputs['q_I_guess'] = q_I_guess 


