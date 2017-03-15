import numpy as np

from ...operation import Operation
from ... import optools

class BgSubtractByTemperature(Operation):
    """
    Find a background spectrum from a batch of background spectra,
    where the temperature of the background spectrum is as close as possible
    to the (input) temperature of the measured spectrum.
    Then subtract that background spectrum from the input spectrum.
    The measured and background spectra are expected to have the same domain.
    """
    
    def __init__(self):
        input_names = ['I_meas','T_meas','bg_batch_output','bg_I_uri','bg_T_uri']
        output_names = ['I_bgsub', 'bg_factor']
        super(BgSubtractByTemperature, self).__init__(input_names, output_names)
        self.input_doc['I_meas'] = 'array of I(q)'
        self.input_doc['T_meas'] = str('temperature as taken from the dict '
        + 'produced by the detector header file')
        self.input_doc['bg_batch_output'] = str('the output (list of dicts) '
        + 'of a batch of background spectra at different temperatures')
        self.input_doc['bg_I_uri'] = str('the uri for the items saved in bg_batch_output '
        + 'containing the background intensity spectrum') 
        self.input_doc['bg_T_uri'] = str('the uri for the items saved in bg_batch_output '
        + 'containing the background spectrum temperatures')
        self.output_doc['I_bgsub'] = 'I_meas - bg_factor * (I_bg)'
        self.output_doc['bg_factor'] = str('correction factor applied to background '
        + 'before subtraction, to ensure positive intensity values')
        self.input_src['I_meas'] = optools.wf_input
        self.input_src['T_meas'] = optools.wf_input
        self.input_src['bg_batch_output'] = optools.wf_input
        self.input_src['bg_I_uri'] = optools.wf_input
        self.input_src['bg_T_uri'] = optools.wf_input
        self.input_type['I_meas'] = optools.ref_type
        self.input_type['T_meas'] = optools.ref_type
        self.input_type['bg_batch_output'] = optools.ref_type
        self.input_type['bg_T_uri'] = optools.path_type
        self.input_type['bg_I_uri'] = optools.path_type

    def run(self):
        I_meas = self.inputs['I_meas']
        T_meas = self.inputs['T_meas']
        bg_I_uri = self.inputs['bg_I_uri']
        bg_T_uri = self.inputs['bg_T_uri']
        bg_out = self.inputs['bg_batch_output']
        T_allbg = [optools.get_uri_from_dict(bg_T_uri,d) for d in bg_out]
        I_allbg = [optools.get_uri_from_dict(bg_I_uri,d) for d in bg_out]
        closest_T_idx = np.argmin(np.abs([T_bg - T_meas for T_bg in T_allbg]))
        I_bg = I_allbg[closest_T_idx]
        #if not all(q_I[:,0] == q_I_bg[:,0]):
        #    msg = 'SPECTRUM AND BACKGROUND ON DIFFERENT q DOMAINS'
        #    raise ValueError(msg)
        bad_data = (I_meas <= 0) | (I_bg <= 0) | np.isnan(I_meas) | np.isnan(I_bg)
        bg_factor = np.min(I_meas[~bad_data] / I_bg[~bad_data])
        #print 'bg factor is {}'.format(bg_factor)
        I_bgsub = I_meas - bg_factor * I_bg
        self.outputs['I_bgsub'] = np.array(I_bgsub)
        self.outputs['bg_factor'] = bg_factor


