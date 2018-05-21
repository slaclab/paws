from __future__ import print_function
from collections import OrderedDict

import numpy as np
from xrsdkit.fitting.xrsd_fitter import XRSDFitter
from xrsdkit.scattering import compute_intensity

from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    source_wavelength=None,
    populations={},
    fixed_params={},
    param_bounds={},
    param_constraints={},
    q_range=[0.,float('inf')],
    error_weighted=True,
    logI_weighted=True)

outputs = OrderedDict(
    populations={},
    report={},
    q_I_opt=None)

class XRSDFit(Operation):
    """Fit scattering equation parameters to measured data.

    Optimizes the parameters of one or several populations of scatterers
    against a measured intensity profile (I(q) vs. q).
    """

    def __init__(self):
        super(XRSDFit, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of wave vectors (1/Angstrom) and intensities (counts)'
        self.input_doc['source_wavelength'] = 'wavelength of light source, in Angstroms'
        self.input_doc['populations'] = 'dict defining populations, xrsdkit format'
        self.input_doc['fixed_params'] = 'dict defining fixed params, xrsdkit format'
        self.input_doc['param_bounds'] = 'dict defining param bounds, xrsdkit format'
        self.input_doc['param_constraints'] = 'dict defining param constraints, xrsdkit format'
        self.input_doc['q_range'] = 'lower and upper q-limits for the fit objective'
        self.output_doc['populations'] = 'populations with parameters optimized'
        self.output_doc['report'] = 'dict reporting optimization results'
        self.output_doc['q_I_opt'] = 'computed intensity for the optimized populations'

        self.input_datatype['populations'] = 'dict'
        self.input_datatype['fixed_params'] = 'dict'
        self.input_datatype['param_bounds'] = 'dict'
        self.input_datatype['param_constraints'] = 'dict'

    def run(self):
        q_I = self.inputs['q_I']
        src_wl = self.inputs['source_wavelength']        
        pops = self.inputs['populations']
        p_fix = self.inputs['fixed_params']
        p_b = self.inputs['param_bounds']
        p_c = self.inputs['param_constraints']
        errwtd = self.inputs['error_weighted']
        logIwtd = self.inputs['logI_weighted']
        qrng = self.inputs['q_range']

        xrf = XRSDFitter(q_I,pops,src_wl)
        fit_pops,rpt = xrf.fit(p_fix,p_b,p_c,errwtd,logIwtd,qrng)

        self.message_callback(xrf.print_report(pops,fit_pops,rpt))
 
        I_opt = compute_intensity(q_I[:,0],fit_pops,src_wl)

        q_I_opt = np.array([q_I[:,0],I_opt]).T
        self.outputs['populations'] = fit_pops 
        self.outputs['report'] = rpt
        self.outputs['q_I_opt'] = q_I_opt

