import numpy as np

from ... import Operation as op
from ...Operation import Operation

class SubtractMaximumBackground(Operation):
    """
    Originally contributed by Amanda Fournier.

    Subtract a background from a foreground, with scaling to prevent over-subtraction.
    Has optional arguments for error vectors (default None).
    """

    def __init__(self):
        input_names = ['q_I', 'q_I_bg', 'dI', 'dI_bg']
        output_names = ['q_I', 'dI', 'bg_factor']
        super(SubtractMaximumBackground, self).__init__(input_names, output_names)
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensity values'
        self.input_doc['q_I_bg'] = 'n-by-2 array, background corresponding to q_I'
        self.input_doc['dI'] = '1d array, error estimate of I (optional, default None)' 
        self.input_doc['dI_bg'] = '1d array, error estimate of I_bg (optional, default None)'
        self.output_doc['q_I'] = 'n-by-2 array of q values and background-subtracted intensity: I-(bg_factor*I_bg)'
        self.output_doc['dI'] = 'error estimate of background-subtracted intensity'
        self.output_doc['bg_factor'] = str('the factor the background was multiplied by '
        + ' before subraction to ensure positive values for output intensity')
        # source & type
        self.input_src['q_I'] = op.wf_input
        self.input_src['q_I_bg'] = op.wf_input
        self.input_src['dI'] = op.wf_input
        self.input_src['dI_bg'] = op.wf_input
        self.input_type['q_I'] = op.ref_type
        self.input_type['q_I_bg'] = op.ref_type
        self.input_type['dI'] = op.none_type
        self.input_type['dI_bg'] = op.none_type

    def run(self):
        q_I = self.inputs['q_I']
        I = q_I[:,1]
        q_I_bg = self.inputs['q_I_bg']
        I_bg = q_I[:,1]
        if not q_I[:,0] == q_I_bg[:,0]:
            raise ValueError('[{}] spectrum and background have different q values.')
        dI = self.inputs['dI']
        dI_bg = self.inputs['dI_bg']
        bad_data = (I < 0) | (I_bg <= 0) | np.isnan(I) | np.isnan(I_bg)
        bg_factor = np.min(I[~bad_data] / I_bg[~bad_data])
        I_out = I-(bg_factor*I_bg)
        if dI_bg is not None and dI is not None:
            err_out = (dI**2+(bg_factor*dI_bg)**2)**0.5
        else:
            err_out = None
        self.outputs['q_I'] = np.array(zip(q_I[:,0],I_out))
        self.outputs['dI'] = err_out
        self.outputs['bg_factor'] = bg_factor
 
