from collections import OrderedDict

from xrsdkit.visualization.gui import run_fit_gui
import numpy as np

from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    system=None,
    error_weighted=True,
    logI_weighted=True,
    q_range=[0.,float('inf')]
    )

outputs = OrderedDict(
    system=None,
    system_dict=None,
    q_I_opt = None
    ) 

class XRSDFitGUI(Operation):
    """Interactively fit a XRSD spectrum."""

    def __init__(self):
        super(XRSDFitGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.input_doc['system'] = 'material system description, as a xrsdkit.system.System'
        self.input_doc['error_weighted'] = 'flag for using I(q) error estimates to weight fit objective'
        self.input_doc['logI_weighted'] = 'flag for evaluating the fit objective on log(I)'
        self.input_doc['q_range'] = 'lower and upper q-limits for the fit objective'
        self.output_doc['system'] = 'xrsdkit.system.System with optimized parameters'
        self.output_doc['system_dict'] = 'output `system`.to_dict()'
        self.output_doc['q_I_opt'] = 'computed intensity for the optimized system'

    def run(self):
        q_I = self.inputs['q_I']
        sys = self.inputs['system']
        err_wtd = self.inputs['error_weighted']
        logI_wtd = self.inputs['logI_weighted']
        q_range = self.inputs['q_range']
        if sys is not None:
            if sys.fit_report:
                err_wtd = sys.fit_report['error_weighted']
                logI_wtd = sys.fit_report['logI_weighted']
                q_range = sys.fit_report['q_range']

        sys_opt = run_fit_gui(
        sys,q_I[:,0],q_I[:,1],None,err_wtd,logI_wtd,q_range) 

        I_opt = sys_opt.compute_intensity(q_I[:,0]) 
        q_I_opt = np.array([q_I[:,0],I_opt]).T

        self.outputs['system'] = sys_opt
        self.outputs['system_dict'] = sys_opt.to_dict()
        self.outputs['q_I_opt'] = q_I_opt
        return self.outputs

