import numpy as np

from ...slacxop import Operation
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
        input_names = ['I_meas','T_meas','bg_batch_output','bg_T_key','bg_I_key']
        output_names = ['I_bgsub', 'bg_factor']
        super(BgSubtractByTemperature, self).__init__(input_names, output_names)
        self.input_doc['I_meas'] = 'array of I(q)'
        self.input_doc['T_meas'] = 'temperature as taken from the dict produced by the detector header file'
        self.input_doc['bg_batch_output'] = 'the output (list of dicts) of a batch of background spectra at different temperatures'
        self.input_doc['bg_T_key'] = str('each dict in bg_batch_output is expected to have this key in it, '
        + 'where the value will represent the temperature of the background spectrum')
        self.input_doc['bg_I_key'] = str('each dict in bg_batch_output is expected to have this key in it, '
        + 'where the value will represent the measured intensity spectrum')
        self.output_doc['I_bgsub'] = 'I_meas - bg_factor * (I_bg)'
        self.output_doc['bg_factor'] = 'correction factor applied to background before subtraction to ensure positive intensity values'
        self.input_src['I_meas'] = optools.wf_input
        self.input_src['T_meas'] = optools.wf_input
        self.input_src['bg_batch_output'] = optools.wf_input
        self.input_src['bg_T_key'] = optools.user_input
        self.input_src['bg_I_key'] = optools.user_input
        self.input_type['bg_T_key'] = optools.str_type
        self.input_type['bg_I_key'] = optools.str_type

    def run(self):
        q_meas = self.inputs['q_meas']
        I_meas = self.inputs['I_meas']
        T_meas = self.inputs['temperature']
        bg_T_key = self.inputs['bg_T_key']
        bg_I_key = self.inputs['bg_I_key']
        bg_out = self.inputs['bg_batch_output']
        T_allbg = [d[bg_T_key] for d in bg_out]
        I_allbg = [d[bg_I_key] for d in bg_out]
        idx = np.argmin(np.abs([T_bg - T_meas for T_bg in T_allbg]))
        I_bg = I_allbg[idx]
        #if not all(q_I[:,0] == q_I_bg[:,0]):
        #    msg = 'SPECTRUM AND BACKGROUND ON DIFFERENT q DOMAINS'
        #    raise ValueError(msg)
        bad_data = I_meas <= 0 | I_bg <= 0 | np.isnan(I_meas) | np.isnan(I_bg)
        bg_factor = np.min(I_meas[~bad_data] / I_bg[~bad_data])
        #print 'bg factor is {}'.format(bg_factor)
        I_bgsub = I_meas - bg_factor * I_bg
        self.outputs['I_bgsub'] = np.array(I_bgsub)
        self.outputs['bg_factor'] = bg_factor

class SubtractMaximumBackground(Operation):
    """Subtract a background from a foreground, with scaling to prevent over-subtraction.

    Has optional arguments for error vectors.  If no error estimate is available, set these to *None*.
    If either error vector is *None*, the output error vector will also be *None*."""
    def __init__(self):
        input_names = ['foreground', 'background', 'foreground_error', 'background_error']
        output_names = ['subtracted', 'subtracted_error', 'factor']
        super(SubtractMaximumBackground, self).__init__(input_names, output_names)
        self.input_doc['foreground'] = '1d ndarray; experimental data'
        self.input_doc['background'] = '1d ndarray; background to subtract, same coordinates as *foreground*'
        self.input_doc['foreground_error'] = '1d ndarray; error estimate of *foreground*; if none available, use *None*'
        self.input_doc['background_error'] = '1d ndarray; error estimate of *background*; if none available, use *None*'
        self.output_doc['subtracted'] = 'background-subtracted experimental data'
        self.output_doc['subtracted_error'] = 'error estimate of *subtracted*'
        self.output_doc['factor'] = 'the factor the background was multiplied by before subraction'
        # source & type
        self.input_src['foreground'] = optools.wf_input
        self.input_src['background'] = optools.wf_input
        self.input_src['foreground_error'] = optools.wf_input
        self.input_src['background_error'] = optools.wf_input

    def run(self):
        self.outputs['subtracted'], self.outputs['subtracted_error'], self.outputs['factor'] = \
            subtract_maximum_background(self.inputs['foreground'], self.inputs['background'],
                                                    self.inputs['foreground_error'], self.inputs['background_error'])

def subtract_maximum_background(foreground, background, foreground_error=None, background_error=None):
    # the constraints on background are minutely stricter because we will divide foreground by it
    bad_data = (foreground < 0) | (background <= 0) | np.isnan(foreground) | np.isnan(background)
    if np.any(bad_data):
        print "There were %i invalid data points in this background subtraction attempt." % np.sum(bad_data)
    factor = np.min(foreground[~bad_data] / background[~bad_data])
    if (factor > 1) or (factor < 0.8):
        print "The background multiplication factor was %f, an unusual value." % factor
    subtracted = foreground - (factor * background)
    if (foreground_error is None) or (background_error is None):
        subtracted_error = None
        # inform user if their input was nonsensical
        if (foreground_error is not None) or (background_error is not None):
            print "Only one of the error vectors is available, so an error estimate will not be output."
    else: # both available
        subtracted_error = (foreground_error ** 2 + (factor * background_error) ** 2) ** 0.5
    return subtracted, subtracted_error, factor




