from __future__ import print_function
from collections import OrderedDict

import numpy as np
from xrsdkit.fitting.xrsd_fitter import XRSDFitter
from xrsdkit.scattering import compute_intensity

from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    populations=None,
    fixed_params=None,
    param_bounds=None,
    param_constraints=None,
    error_weighted=True,
    logI_weighted=True,
    logq_weighted=False,
    source_wavelength=None)

outputs = OrderedDict(
    populations=None,
    report=None,
    q_I_opt=None)

class XRSDFit(Operation):
    """Fit scattering equation parameters to measured data.

    Optimizes the parameters of one or several populations of scatterers
    against a measured intensity profile (I(q) vs. q).
    """

    def __init__(self):
        super(XRSDFit, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of wave vectors (1/Angstrom) and intensities (counts)'
        self.input_doc['populations'] = 'dict specifying '\
            'scatterer populations and initial guesses for parameters, '\
            'formatted according to the xrsdkit specifications'
        self.input_doc['fixed_params'] = 'dict indicating which parameters '\
            'should be held fixed during optimization, '\
            'where the dict structure mirrors `populations`, '\
            'but with boolean values'
        self.input_doc['param_bounds'] = 'like `fixed_params`, '\
            'but with tuple values specifying '\
            'the lower and upper parameter bounds'
        self.input_doc['param_constraints'] = 'like `fixed_params`, '\
            'but with expressions (strings) as values, '\
            'where the expressions define the constraints '\
            'according to the xrsdkit specifications'
        self.input_doc['source_wavelength'] = 'wavelength '\
            'of x-ray source, in Angstroms'

        self.output_doc['populations'] = 'similar to input `populations`, '\
            'but with the optimized parameters'
        self.output_doc['report'] = 'dict expressing '\
            'the numerical results of the optimization'
        self.output_doc['q_I_opt'] = 'n-by-2 array '\
            'of q and the optimized computed intensity profile'
        self.input_datatype['populations'] = 'dict'
        self.input_datatype['fixed_params'] = 'dict'
        self.input_datatype['param_bounds'] = 'dict'
        self.input_datatype['param_constraints'] = 'dict'

    def run(self):
        q_I = self.inputs['q_I']
        pops = self.inputs['populations']
        p_fix = self.inputs['fixed_params']
        p_b = self.inputs['param_bounds']
        p_c = self.inputs['param_constraints']
        errwtd = self.inputs['error_weighted']
        logIwtd = self.inputs['logI_weighted']
        logqwtd = self.inputs['logq_weighted']
        src_wl = self.inputs['source_wavelength']        

        xrf = XRSDFitter(q_I,pops,src_wl)
        fit_pops,rpt = xrf.fit(p_fix,p_b,p_c,errwtd,logIwtd,logqwtd)

        if self.message_callback:
            self.message_callback(xrf.print_report(pops,fit_pops,rpt))
 
        I_opt = compute_intensity(q_I[:,0],fit_pops,src_wl)

        from matplotlib import pyplot as plt
        I_guess = compute_intensity(q_I[:,0],pops,src_wl)
        plt.figure(2)
        plt.semilogy(q_I[:,0],q_I[:,1],'k')
        plt.semilogy(q_I[:,0],I_guess,'r')
        plt.semilogy(q_I[:,0],I_opt,'g')
        plt.show()

        q_I_opt = np.array([q_I[:,0],I_opt]).T
        self.outputs['populations'] = fit_pops 
        self.outputs['report'] = rpt
        self.outputs['q_I_opt'] = q_I_opt

