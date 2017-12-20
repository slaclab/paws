import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation
from ... import optools

inputs = OrderedDict(
    q_I_meas=None,
    T_meas=None,
    bg_batch_outputs=None,
    q_I_bg_key=None,
    T_bg_key=None)
outputs = OrderedDict(
    q_I_bgsub=None,
    T_bg=None,
    bg_factor=None)

class BgSubtractByTemperature(Operation):
    """
    Find a background spectrum from a batch of background spectra,
    where the temperature of the background spectrum is as close as possible
    to the (input) temperature of the measured spectrum.
    Then subtract that background spectrum from the input spectrum.
    The measured and background spectra are expected to have the same domain.

    Operation originally contributed by Amanda Fournier.  
    """
    
    def __init__(self):
        super(BgSubtractByTemperature, self).__init__(inputs, outputs)
        self.input_doc['q_I_meas'] = 'n-by-2 array of I(q) versus q'
        self.input_doc['T_meas'] = 'temperature as taken from the dict '\
            'produced by the detector header file'
        self.input_doc['bg_batch_outputs'] = 'the output (list of dicts) '\
            'of a batch of background spectra at different temperatures'
        self.input_doc['q_I_bg_key'] = 'the name of the bg_batch workflow output '\
            'containing n-by-2 array of q and I(q) for the background spectra '
        self.input_doc['T_bg_key'] = 'the name of the bg_batch workflow output '\
            'containing the background spectrum temperatures'
        self.output_doc['q_I_bgsub'] = 'n-by-2 array of q and '\
            'background-subracted intensity (I_meas-bg_factor*I_bg)'
        self.output_doc['T_bg'] = 'temperature of the subtracted background spectrum'
        self.output_doc['bg_factor'] = 'correction factor applied to background '\
            'before subtraction, to ensure positive background-subtracted intensities'

    def run(self):
        q_I_meas = self.inputs['q_I_meas']
        T_meas = self.inputs['T_meas']
        qIkey = self.inputs['q_I_bg_key']
        Tkey = self.inputs['T_bg_key']
        bg_out = self.inputs['bg_batch_outputs']
        T_allbg = [d[Tkey] for d in bg_out]
        closest_T_idx = np.argmin(np.abs([T_bg - T_meas for T_bg in T_allbg]))
        T_bg = T_allbg[closest_T_idx]
        q_I_bg = bg_out[closest_T_idx][qIkey]
        if not all(q_I_meas[:,0] == q_I_bg[:,0]):
            msg = 'SPECTRUM AND BACKGROUND ON DIFFERENT q DOMAINS'
            raise ValueError(msg)
        bad_data = ( (q_I_meas[:,1] <= 0) 
            | (q_I_bg[:,1] <= 0) 
            | np.isnan(q_I_meas[:,1]) 
            | np.isnan(q_I_bg[:,1]) )
        I_floor = 0 
        #I_floor = 1E-6 * np.max(q_I_meas[:,1])
        bg_factor = np.min((q_I_meas[:,1][~bad_data]-I_floor) / q_I_bg[:,1][~bad_data])
        q_I_bgsub = np.array(q_I_meas)
        q_I_bgsub[:,1] = q_I_meas[:,1] - bg_factor * q_I_bg[:,1]

        self.outputs['q_I_bgsub'] = q_I_bgsub
        self.outputs['T_bg'] = T_bg 
        self.outputs['bg_factor'] = bg_factor


