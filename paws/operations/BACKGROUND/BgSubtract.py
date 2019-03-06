import numpy as np
from collections import OrderedDict

from ..Operation import Operation

inputs = OrderedDict(
    q_I = None,
    q_I_bg = None,
    dI = None,
    dI_bg = None)
outputs = OrderedDict(
    q_I_bgsub = None,
    dI = None,
    bg_factor = None)

class BgSubtract(Operation):
    """Background subtraction for 1-d spectra (intensity versus q).

    Subtracts the background from an image,
    after scaling the background to prevent over-subtraction.
    Given error estimates for the image and background, 
    estimates the error for the background-subtracted intensity. 
    """

    def __init__(self):
        super(BgSubtract, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensity values'
        self.input_doc['q_I_bg'] = 'n-by-2 array, background corresponding to q_I'
        self.input_doc['dI'] = '1d array, error estimate of I (optional, default None)' 
        self.input_doc['dI_bg'] = '1d array, error estimate of I_bg (optional, default None)'
        self.output_doc['q_I_bgsub'] = 'n-by-2 array of q values and background-subtracted intensity: I-(bg_factor*I_bg)'
        self.output_doc['dI'] = 'error estimate of background-subtracted intensity'
        self.output_doc['bg_factor'] = 'the factor the background was multiplied by '\
            'before subraction to ensure positive values for output intensity'

    def run(self):
        q_I = self.inputs['q_I']
        q_I_bg = self.inputs['q_I_bg']
        I = q_I[:,1]
        I_bg = q_I_bg[:,1]
        bad_data = (I < 0) | (I_bg <= 0) | np.isnan(I) | np.isnan(I_bg)
        bg_factor = np.min(I[~bad_data] / I_bg[~bad_data])
        #if bg_factor > 1.: bg_factor = 1.
        self.message_callback('subtracting background (bg multiplier: {})'.format(bg_factor))
        I_out = I-(bg_factor*I_bg)
        dI = self.inputs['dI']
        dI_bg = self.inputs['dI_bg']
        dI_out = None
        if dI_bg is not None and dI is not None:
            dI_out = (dI**2+(bg_factor*dI_bg)**2)**0.5
        q_I_bgsub = np.zeros(q_I.shape)
        q_I_bgsub[:,0] = q_I[:,0]
        q_I_bgsub[:,1] = I_out
        self.outputs['q_I_bgsub'] = q_I_bgsub 
        self.outputs['dI'] = dI_out
        self.outputs['bg_factor'] = bg_factor
        return self.outputs

