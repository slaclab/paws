from collections import OrderedDict
import copy

import numpy as np
from scipy.optimize import curve_fit

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools.saxs import saxs_fit

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
        input_names = ['q_I','flags','params','fixed_params']#,'objfun','constraints']
        output_names = ['params','q_I_opt']
        super(SpectrumFit, self).__init__(input_names, output_names)
        self.input_doc['q_I'] = 'n-by-2 array of wave vectors (1/Angstrom) and intensities (counts)'
        self.input_doc['flags'] = 'dict of flags indicating what populations to fit'
        self.input_doc['params'] = 'dict of initial values for the scattering equation parameters '\
            'for each of the populations specified in the input flags'
        self.input_doc['fixed_params'] = 'list of strings (keys) indicating '\
            'which parameters to hold fixed during optimization'
        #self.input_doc['objfun'] = 'string indicating objective function for optimization- '\
        #    'see documentation of tools.saxs.saxs_fit.fit_spectrum() for supported objective functions'
        #self.input_doc['constraints'] = 'list of strings indicating constraints- '\
        #    'see documentation of tools.saxs.saxs_fit.fit_spectrum() for supported constraints'
        self.output_doc['params'] = 'dict of scattering equation parameters copied from inputs, '\
            'with values optimized for all keys not listed in fixed_params'
        self.output_doc['q_I_opt'] = 'n-by-2 array of q and the optimized computed intensity spectrum'
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.input_type['params'] = opmod.workflow_item
        self.inputs['fixed_params'] = [] 

    def run(self):
        q_I = self.inputs['q_I']
        f = self.inputs['flags']
        p = self.inputs['params']
        fixkeys = self.inputs['fixed_params']
        if not f['bad_data']:
            p_opt = saxs_fit.fit_spectrum(q_I,f,p,fixkeys,'chi2log')
            I_opt = saxs_fit.compute_saxs(q_I[:,0],f,p_opt)
            q_I_opt = np.array([q_I[:,0],I_opt]).T
            self.outputs['params'] = p_opt 
            self.outputs['q_I_opt'] = q_I_opt

