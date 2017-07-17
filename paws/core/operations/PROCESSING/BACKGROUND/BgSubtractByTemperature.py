import numpy as np

from ... import Operation as op
from ...Operation import Operation
from ... import optools

class BgSubtractByTemperature(Operation):
    """
    Originally contributed by Amanda Fournier.  

    Find a background spectrum from a batch of background spectra,
    where the temperature of the background spectrum is as close as possible
    to the (input) temperature of the measured spectrum.
    Then subtract that background spectrum from the input spectrum.
    The measured and background spectra are expected to have the same domain.
    """
    
    def __init__(self):
        input_names = ['q_I_meas','T_meas','bg_batch_output','bg_I_uri','bg_T_uri']
        output_names = ['q_I_bgsub', 'T_bg', 'bg_factor']
        super(BgSubtractByTemperature, self).__init__(input_names, output_names)
        self.input_doc['q_I_meas'] = 'n-by-2 array of I(q) versus q'
        self.input_doc['T_meas'] = str('temperature as taken from the dict '
        + 'produced by the detector header file')
        self.input_doc['bg_batch_output'] = str('the output (list of dicts) '
        + 'of a batch of background spectra at different temperatures')
        self.input_doc['bg_I_uri'] = str('the uri for the items saved in bg_batch_output '
        + 'containing the background intensity spectrum, expected to be on same q domain as q_I_meas') 
        self.input_doc['bg_T_uri'] = str('the uri for the items saved in bg_batch_output '
        + 'containing the background spectrum temperatures')
        self.output_doc['q_I_bgsub'] = 'n by 2 array of q and background subracted intensity (I_meas-bg_factor*I_bg)'
        self.output_doc['T_bg'] = 'Temperature of the subtracted background spectrum'
        self.output_doc['bg_factor'] = str('correction factor applied to background '
        + 'before subtraction, to ensure positive intensity values')
        self.input_src['q_I_meas'] = op.wf_input
        self.input_src['T_meas'] = op.wf_input
        self.input_src['bg_batch_output'] = op.wf_input
        self.input_src['bg_I_uri'] = op.wf_input
        self.input_src['bg_T_uri'] = op.wf_input
        self.input_type['q_I_meas'] = op.ref_type
        self.input_type['T_meas'] = op.ref_type
        self.input_type['bg_batch_output'] = op.ref_type
        self.input_type['bg_T_uri'] = op.path_type
        self.input_type['bg_I_uri'] = op.path_type

    def run(self):
        q_I_meas = self.inputs['q_I_meas']
        q_I_bgsub = np.array(q_I_meas)
        T_meas = self.inputs['T_meas']
        bg_I_uri = self.inputs['bg_I_uri']
        bg_T_uri = self.inputs['bg_T_uri']
        bg_out = self.inputs['bg_batch_output']
        T_allbg = [optools.get_uri_from_dict(bg_T_uri,d) for d in bg_out]
        closest_T_idx = np.argmin(np.abs([T_bg - T_meas for T_bg in T_allbg]))
        T_bg = T_allbg[closest_T_idx]
        I_bg = optools.get_uri_from_dict(bg_I_uri,bg_out[closest_T_idx])
        #if not all(q_I[:,0] == q_I_bg[:,0]):
        #    msg = 'SPECTRUM AND BACKGROUND ON DIFFERENT q DOMAINS'
        #    raise ValueError(msg)
        bad_data = (q_I_meas[:,1] <= 0) | (I_bg <= 0) | np.isnan(q_I_meas[:,1]) | np.isnan(I_bg)
        I_floor = 0 
        #I_floor = 1E-6 * np.max(q_I_meas[:,1])
        bg_factor = np.min((q_I_meas[:,1][~bad_data]-I_floor) / I_bg[~bad_data])
        #print 'bg factor is {}'.format(bg_factor)
        q_I_bgsub[:,1] = q_I_meas[:,1] - bg_factor * I_bg

        #from matplotlib import pyplot as plt
        #plt.figure(1)
        #plt.semilogy(q_I_meas[:,0],q_I_meas[:,1])
        #plt.semilogy(q_I_meas[:,0],I_bg,'r')
        #plt.semilogy(q_I_bgsub[:,0],q_I_bgsub[:,1],'g')
        #plt.legend(['sample','bg','(sample - bg)'],loc=4)
        #print bg_factor
        #plt.show()

        self.outputs['q_I_bgsub'] = q_I_bgsub
        self.outputs['T_bg'] = T_bg 
        self.outputs['bg_factor'] = bg_factor


