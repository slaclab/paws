from collections import OrderedDict

from xrsdkit.visualization.gui import run_fit_gui
import numpy as np

from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    source_wavelength=None,
    system=None,
    error_weighted=True,
    logI_weighted=True,
    q_range=[0.,float('inf')],
    good_fit_prior=False)

outputs = OrderedDict(
    system=None,
    system_dict=None,
    q_I_opt = None,
    good_fit_flag=False) 

class XRSDFitGUI(Operation):
    """Interactively fit a XRSD spectrum."""

    def __init__(self):
        super(XRSDFitGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.input_doc['source_wavelength'] = 'wavelength of light source, in Angstroms'
        self.input_doc['system'] = 'material system description, as a xrsdkit.system.System'
        self.input_doc['error_weighted'] = 'flag for using I(q) error estimates to weight fit objective'
        self.input_doc['logI_weighted'] = 'flag for evaluating the fit objective on log(I)'
        self.input_doc['q_range'] = 'lower and upper q-limits for the fit objective'
        self.input_doc['good_fit_prior'] = 'initial setting for the good fit indicator'
        self.output_doc['system'] = 'xrsdkit.system.System with optimized parameters'
        self.output_doc['system_dict'] = 'output `system`.to_dict()'
        self.output_doc['q_I_opt'] = 'computed intensity for the optimized system'
        self.output_doc['good_fit_flag'] = 'flag indicating user satisfaction with the fit'

    def run(self):
        q_I = self.inputs['q_I']
        src_wl = self.inputs['source_wavelength']
        sys = self.inputs['system']
        err_wtd = self.inputs['error_weighted']
        logI_wtd = self.inputs['logI_weighted']
        q_range = self.inputs['q_range']
        good_fit_prior = self.inputs['good_fit_prior']
        if sys is not None:
            if sys.fit_report:
                err_wtd = sys.fit_report['error_weighted']
                logI_wtd = sys.fit_report['logI_weighted']
                q_range = sys.fit_report['q_range']

        sys_opt, good_fit_flag = run_fit_gui(
        sys,q_I[:,0],q_I[:,1],src_wl,None,err_wtd,logI_wtd,q_range,good_fit_prior) 

        I_opt = sys_opt.compute_intensity(q_I[:,0],src_wl) 
        q_I_opt = np.array([q_I[:,0],I_opt]).T

        self.outputs['system'] = sys_opt
        self.outputs['system_dict'] = sys_opt.to_dict()
        self.outputs['q_I_opt'] = q_I_opt
        self.outputs['good_fit_flag'] = good_fit_flag 
        return self.outputs

