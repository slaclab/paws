from collections import OrderedDict
import copy

import numpy as np
from scipy.optimize import curve_fit

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class SpectrumFit(Operation):
    """
    Use a measured SAXS spectrum (I(q) vs. q),
    to optimize the parameters of a theoretical SAXS spectrum
    for one or several populations of scatterers. 
    Works by minimizing an objective function that compares
    the measured spectrum against the theoretical result.
    TODO: document the algorithm here.

    Input arrays of q and I(q), 
    a string indicating choice of objective function, 
    a dict of features describing the spectrum,
    and a list of strings indicating which keys in the dict 
    should be used as optimization parameters.
    The input features dict includes initial fit parameters
    as well as the flags indicating which populations to include.
    The features dict is of the same format as
    SpectrumProfiler and SpectrumParameterization outputs.

    Outputs a return code and the features dict,
    with entries updated for the optimized parameters.
    Also returns the theoretical result for I(q),
    and a renormalized measured spectrum for visual comparison.
    """

    def __init__(self):
        input_names = ['q_I','flags','params','fit_params','objfun']
        output_names = ['params','q_I_opt']
        super(SpectrumFit, self).__init__(input_names, output_names)
        self.input_doc['q_I'] = 'n-by-2 array of wave vectors (1/Angstrom) and intensities (counts)'
        self.input_doc['flags'] = 'dict of flags indicating what populations to fit'
        self.input_doc['params'] = 'dict of initial values for the scattering equation parameters '\
            'for each of the populations specified in the input flags'
        self.input_doc['fit_params'] = 'list of strings (keys) indicating which parameters to optimize'
        self.input_doc['objfun'] = 'string indicating objective function for optimization: '\
        + 'see documentation of saxstools.fit_spectrum() for supported objective functions'
        self.output_doc['params'] = 'dict of scattering equation parameters copied from inputs, '\
        'with values optimized for all keys specified in fit_params'
        self.output_doc['q_I_opt'] = 'n-by-2 array of q and the optimized computed intensity spectrum'
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.input_type['params'] = opmod.workflow_item
        self.inputs['objfun'] = 'chi2log' 

    def run(self):
        f = self.inputs['flags']
        q_I = self.inputs['q_I']
        q = q_I[:,0]
        I = q_I[:,1]
        m = self.inputs['objfun']
        p = self.inputs['params']
        fitkeys = self.inputs['fit_params']
        if f is None or q is None or I is None or fitkeys is None:
            return
        if f['bad_data'] or not any([f['precursor_scattering'],f['form_factor_scattering'],f['diffraction_peaks']]):
            return
        if f['diffraction_peaks']:
            self.outputs['params'] = {'ERROR_MESSAGE':'diffraction peak fitting not yet supported'}
            return
        #p_opt = copy.deepcopy(p)

        # Set up constraints as needed
        c = []
        if f['form_factor_scattering'] or f['diffraction_peaks']:
            c = ['fix_I0']

        # Fitting happens here
        p_opt = saxstools.fit_spectrum(q,I,m,f,p,fitkeys,c)

        I_opt = saxstools.compute_saxs(q,f,p_opt)

        nz = ((I>0)&(I_opt>0))
        logI_nz = np.log(I[nz])
        logIopt_nz = np.log(I_opt[nz])
        Imean = np.mean(logI_nz)
        Istd = np.std(logI_nz)
        logI_nz_s = (logI_nz - Imean) / Istd
        logIopt_nz_s = (logIopt_nz - Imean) / Istd

        q_I_opt = np.array([q,I_opt]).T
        self.outputs['params'] = p_opt 
        self.outputs['q_I_opt'] = q_I_opt

