from __future__ import print_function
from collections import OrderedDict

import numpy as np
from xrsdkit import system as xrsdsys

from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    source_wavelength=None,
    system=None,
    error_weighted=True,
    logI_weighted=True,
    q_range=[0.,float('inf')]) 

outputs = OrderedDict(
    system=None,
    system_dict=None,
    q_I_opt=None)

class XRSDFit(Operation):
    """Fit scattering equation parameters to measured data.

    Optimizes the parameters of a material system (xrsdkit.system.System) 
    against a measured intensity profile (I(q) vs. q).
    """

    def __init__(self):
        super(XRSDFit, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of wave vectors (1/Angstrom) and intensities (counts)'
        self.input_doc['source_wavelength'] = 'wavelength of light source, in Angstroms'
        self.input_doc['system'] = 'material system description, as a xrsdkit.system.System'
        self.input_doc['error_weighted'] = 'flag for using I(q) error estimates to weight fit objective'
        self.input_doc['logI_weighted'] = 'flag for evaluating the fit objective on log(I)'
        self.input_doc['q_range'] = 'lower and upper q-limits for the fit objective'
        self.output_doc['system'] = 'xrsdkit.system.System with optimized parameters'
        self.output_doc['q_I_opt'] = 'computed intensity for the optimized system'

    def run(self):
        q_I = self.inputs['q_I']
        src_wl = self.inputs['source_wavelength']        
        sys = self.inputs['system']
        err_wtd = self.inputs['error_weighted']
        logI_wtd = self.inputs['logI_weighted']
        q_range = self.inputs['q_range']
        if sys is not None:
            if sys.fit_report:
                err_wtd = sys.fit_report['error_weighted']
                logI_wtd = sys.fit_report['logI_weighted']
                q_range = sys.fit_report['q_range']

        self.message_callback('fitting pattern')
        sys_opt = xrsdsys.fit(sys,q_I[:,0],q_I[:,1],src_wl,None,err_wtd,logI_wtd,q_range)
        self.message_callback('done (objective: {} --> {})'.format(
            sys_opt.fit_report['initial_objective'],sys_opt.fit_report['final_objective']))

        # TODO: update report to new xrsdkit API
        #self.message_callback(xrf.print_report(pops,fit_pops,rpt))
 
        I_opt = sys_opt.compute_intensity(q_I[:,0],src_wl) 
        q_I_opt = np.array([q_I[:,0],I_opt]).T

        self.outputs['system'] = sys_opt 
        self.outputs['system_dict'] = sys_opt.to_dict()
        self.outputs['q_I_opt'] = q_I_opt
        return self.outputs

