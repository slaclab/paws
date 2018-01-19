from __future__ import print_function
from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_math, saxs_fit

inputs = OrderedDict(
    q_I=None,
    populations=None,
    params=None,
    fixed_params=None)
outputs = OrderedDict(
    params=None,
    report=None,
    q_I_opt=None)

class SpectrumFit(Operation):
    """Fit scattering equation parameters to measured data.

    Use a measured SAXS spectrum (I(q) vs. q),
    to optimize the parameters of a theoretical SAXS spectrum
    for one or several populations of scatterers. 
    Works by minimizing an objective function that compares
    the measured spectrum against the theoretical result.
    """

    def __init__(self):
        super(SpectrumFit, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of wave vectors (1/Angstrom) and intensities (counts)'
        self.input_doc['populations'] = 'dict that counts scatterer populations'
        self.input_doc['params'] = '(optional) dict of parameters '\
            'used as initial condition for fit optimization. '\
            'defaults are chosen if not provided.'
        self.input_doc['fixed_params'] = 'dict (subset of `params`) '\
            'indicating which `params` should be fixed during optimization'
        self.output_doc['params'] = 'dict of scattering equation parameters, '\
            'with values optimized for all keys not listed in fixed_params'
        self.output_doc['report'] = 'dict expressing the objective function, '\
            'and its evaluation at the initial and final points of the fit'
        self.output_doc['q_I_opt'] = 'n-by-2 array of q and the optimized computed intensity spectrum'
        self.input_datatype['populations'] = 'dict'
        self.input_datatype['params'] = 'dict'
        self.input_datatype['fixed_params'] = 'dict'

    def run(self):
        q_I = self.inputs['q_I']
        pops = self.inputs['populations']
        pars = self.inputs['params']
        p_fix = self.inputs['fixed_params']
        
        all_pops = OrderedDict.fromkeys(saxs_math.population_keys)
        all_pops.update(pops)
        sxf = saxs_fit.SaxsFitter(q_I,all_pops)
        p_opt,rpt = sxf.fit(pars,p_fix,'chi2log')

        q_I_opt = None
        if not bool(all_pops['unidentified']) \
        and not bool(all_pops['diffraction_peaks']):
            I_opt = saxs_math.compute_saxs(q_I[:,0],all_pops,p_opt)
            q_I_opt = np.array([q_I[:,0],I_opt]).T
        self.outputs['params'] = p_opt 
        self.outputs['report'] = rpt
        self.outputs['q_I_opt'] = q_I_opt

