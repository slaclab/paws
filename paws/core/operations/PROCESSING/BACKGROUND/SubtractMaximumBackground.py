import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

class SubtractMaximumBackground(Operation):
    """
    Subtract a background from a foreground, with scaling to prevent over-subtraction.
    Optionally, input an intensity error array, 
    and get an error estimate for the background-subtracted intensity. 

    Operation originally contributed by Amanda Fournier.
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
        self.output_doc['bg_factor'] = 'the factor the background was multiplied by '\
        ' before subraction to ensure positive values for output intensity'
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['q_I_bg'] = opmod.workflow_item

    def run(self):
        q_I = self.inputs['q_I']
        q_I_bg = self.inputs['q_I_bg']
        if q_I is None or q_I_bg is None:
            return 
        if not all(q_I[:,0] == q_I_bg[:,0]):
            msg = 'SPECTRUM AND BACKGROUND ON DIFFERENT q DOMAINS'
            raise ValueError(msg)
        I = q_I[:,1]
        I_bg = q_I[:,1]
        bad_data = (I < 0) | (I_bg <= 0) | np.isnan(I) | np.isnan(I_bg)
        bg_factor = np.min(I[~bad_data] / I_bg[~bad_data])
        I_out = I-(bg_factor*I_bg)
        dI = self.inputs['dI']
        dI_bg = self.inputs['dI_bg']
        dI_out = None
        if dI_bg is not None and dI is not None:
            dI_out = (dI**2+(bg_factor*dI_bg)**2)**0.5
        self.outputs['q_I'] = np.array(zip(q_I[:,0],I_out))
        self.outputs['dI'] = dI_out
        self.outputs['bg_factor'] = bg_factor
 
