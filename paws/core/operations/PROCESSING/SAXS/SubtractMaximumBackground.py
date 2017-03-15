import numpy as np

from ...operation import Operation
from ... import optools

class SubtractMaximumBackground(Operation):
    """
    Subtract a background from a foreground, with scaling to prevent over-subtraction.
    Has optional arguments for error vectors (default None).
    """

    def __init__(self):
        input_names = ['q', 'I', 'I_bg', 'dI', 'dI_bg']
        output_names = ['I', 'dI', 'bg_factor']
        super(SubtractMaximumBackground, self).__init__(input_names, output_names)
        self.input_doc['q'] = '1d array, scattering vector q'
        self.input_doc['I'] = '1d array, intensity at q'
        self.input_doc['I_bg'] = '1d array, same size as q, background intensity at q'
        self.input_doc['dI'] = '1d array, error estimate of I (default None)' 
        self.input_doc['dI_background'] = '1d array, error estimate of I_bg (default None)'
        self.output_doc['I'] = 'output (background-subtracted) intensity = I-(bg_factor*I_bg)'
        self.output_doc['dI'] = 'error estimate of output intensity'
        self.output_doc['bg_factor'] = str('the factor the background was multiplied by '
        + ' before subraction to ensure positive values for output intensity'
        # source & type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['I_bg'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.input_src['dI_bg'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['I_bg'] = optools.ref_type
        self.input_type['dI'] = optools.ref_type
        self.input_type['dI_bg'] = optools.ref_type

    def run(self):
        q = self.inputs['q']
        I = self.inputs['I']
        I_bg = self.inputs['I_bg']
        dI = self.inputs['dI']
        dI_bg = self.inputs['dI_bg']
        bad_data = (I < 0) | (I_bg <= 0) | np.isnan(I) | np.isnan(I_bg)
        bg_factor = np.min(I[~bad_data] / I_bg[~bad_data])
        I_out = I-(bg_factor*I_bg)
        err_out = (dI**2+(bg_factor*dI_bg)**2)**0.5
        self.outputs['I'] = I_out
        self.outputs['dI'] = err_out
        self.outputs['bg_factor'] = bg_factor
 
