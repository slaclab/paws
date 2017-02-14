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
        self.input_doc['T_meas'] = 'temperature as taken from the dict produced by the detector header file'
        self.input_doc['bg_batch_output'] = 'the output (list of dicts) of a batch of background spectra at different temperatures'
        self.input_doc['bg_I_uri'] = 'the uri for the items saved in bg_batch_output containing the background intensity spectrum' 
        self.input_doc['bg_T_uri'] = 'the uri for the items saved in bg_batch_output containing the background spectrum temperatures'
        self.output_doc['I_bgsub'] = 'I_meas - bg_factor * (I_bg)'
        self.output_doc['bg_factor'] = 'correction factor applied to background before subtraction to ensure positive intensity values'
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

class SubtractMaximumBackground(Operation):
    """Subtract a background from a foreground, with scaling to prevent over-subtraction.

    Has optional arguments for error vectors.  If no error estimate is available, set these to *None*.
    If either error vector is *None*, the output error vector will also be *None*.

    Can also, optionally, window to a region in q."""
    def __init__(self):
        input_names = ['q_foreground', 'q_background', 'I_foreground', 'I_background', 'dI_foreground', 'dI_background', 'q_min', 'q_max']
        output_names = ['I_subtracted', 'dI_subtracted', 'factor', 'q']
        super(SubtractMaximumBackground, self).__init__(input_names, output_names)

        self.input_doc['I_foreground'] = '1d ndarray; experimental data'
        self.input_doc['I_background'] = '1d ndarray; background to subtract, same coordinates as *foreground*'
        self.input_doc['dI_foreground'] = '1d ndarray; error estimate of *foreground*; if none available, use *None*'
        self.input_doc['dI_background'] = '1d ndarray; error estimate of *background*; if none available, use *None*'
        self.output_doc['I_subtracted'] = 'background-subtracted experimental data'
        self.output_doc['dI_subtracted'] = 'error estimate of *subtracted*'
        self.output_doc['factor'] = 'the factor the background was multiplied by before subraction'
        # source & type
        self.input_src['q_foreground'] = optools.wf_input
        self.input_src['q_background'] = optools.wf_input
        self.input_src['I_foreground'] = optools.wf_input
        self.input_src['I_background'] = optools.wf_input
        self.input_src['dI_foreground'] = optools.wf_input
        self.input_src['dI_background'] = optools.wf_input
        self.input_src['q_min'] = optools.text_input
        self.input_src['q_max'] = optools.text_input
        self.input_type['q_min'] = optools.float_type
        self.input_type['q_max'] = optools.float_type
        # defaults
        self.inputs['q_min'] = 0.02
        self.inputs['q_max'] = 0.7


    def run(self):
        q_b = self.inputs['q_background']
        q_f = self.inputs['q_foreground']
        I_b = self.inputs['I_background']
        I_f = self.inputs['I_foreground']
        dI_b = self.inputs['dI_background']
        dI_f = self.inputs['dI_foreground']
        q1 = self.inputs['q_min']
        q2 = self.inputs['q_max']
        self.outputs['q'], self.outputs['I_subtracted'], self.outputs['dI_subtracted'], self.outputs['factor'] = \
            subtract_maximum_background(q_f, q_b, I_f, I_b, dI_f, dI_b, q1, q2)


def subtract_maximum_background(q_f, q_b, I_f, I_b, dI_f=None, dI_b=None, q1=None, q2=None):
    if (q_f != q_b).any():
        raise ValueError('Whoah, cannot currently deal with differing q domains, man.')
    if (q1 is not None) and (q2 is not None):
        legit = (q_f >= q1) & (q_f <= q2)
    elif q1 is not None:
        legit = (q_f >= q1)
    elif q2 is not None:
        legit = (q_f <= q2)
    else:
        legit = np.ones(q_f.shape, dtype=bool)
    q = q_f[legit]
    I_f = I_f[legit]
    I_b = I_b[legit]
    if dI_f is not None:
        dI_f = dI_f[legit]
    if dI_b is not None:
        dI_b = dI_b[legit]
    # the constraints on background are minutely stricter because we will divide foreground by it
    bad_data = (I_f < 0) | (I_b <= 0) | np.isnan(I_f) | np.isnan(I_b)
    if np.any(bad_data):
        print "There were %i invalid data points in this background subtraction attempt." % np.sum(bad_data)
    factor = np.min(I_f[~bad_data] / I_b[~bad_data])
    if (factor > 1) or (factor < 0.8):
        print "The background multiplication factor was %f, an unusual value." % factor
    subtracted = I_f - (factor * I_b)
    if (dI_f is None) or (dI_b is None):
        subtracted_error = None
        # inform user if their input was nonsensical
        if (dI_f is not None) or (dI_b is not None):
            print "Only one of the error vectors is available, so an error estimate will not be output."
    else: # both available
        subtracted_error = (dI_f ** 2 + (factor * dI_b) ** 2) ** 0.5
    return q, subtracted, subtracted_error, factor







