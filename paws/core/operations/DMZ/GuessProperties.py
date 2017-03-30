from os.path import join

import numpy as np
from scipy import interp

from ...operation import Operation
from ... import optools

class GuessProperties(Operation):
    """Guess the polydispersity, mean size, and amplitude of spherical diffraction pattern.

    Assumes the data have already been background subtracted, smoothed, and otherwise cleaned."""

    def __init__(self):
        input_names = ['q', 'I', 'dI']
        output_names = ['parameter_guesses','good_flag','detailed_flags','I_guess','q_I_guess','additional_information']
        super(GuessProperties, self).__init__(input_names, output_names)
        # Documentation
        self.input_doc['q'] = '1d ndarray; wave vector values'
        self.input_doc['I'] = '1d ndarray; intensity values'
        self.input_doc['dI'] = '1d ndarray; error estimate of intensity values; input None if no dI exists'
        self.output_doc['parameter_guesses'] = 'dictionary containing guessed parameters mean_size, amplitude_at_zero, and fractional_variation'
        self.output_doc['additional_information'] = 'dictionary of information primarily useful for debug purposes' #'qFirstDip','heightFirstDip','sigmaScaledFirstDip','heightAtZero',dips, shoulders
        self.output_doc['good_flag'] = 'presently a placeholder boolean'
        self.output_doc['detailed_flags'] = 'presently a placeholder dictionary'
        # Source and type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['dI'] = optools.ref_type


    def run(self):
        q, I, dI = self.inputs['q'], self.inputs['I'], self.inputs['dI']
        fractional_variation, qFirstDip, heightFirstDip, sigmaScaledFirstDip, heightAtZero, dips, shoulders = \
            guess_polydispersity(q, I, dI)
        self.outputs['additional_information'] = {'qFirstDip':qFirstDip, 'sigmaScaledFirstDip':sigmaScaledFirstDip,
                                  'heightFirstDip':heightFirstDip, 'dips':dips, 'shoulders':shoulders}
        mean_size = guess_size(fractional_variation, qFirstDip)
        amplitude_at_zero = polydispersity_metric_heightAtZero(qFirstDip, q, I, dI)
        amplitude_at_zero, mean_size, fractional_variation = refine_guess(q, I, amplitude_at_zero, mean_size, fractional_variation, qFirstDip, heightFirstDip)
        self.outputs['parameter_guesses'] = {'fractional_variation':fractional_variation, 'mean_size':mean_size, 'amplitude_at_zero':amplitude_at_zero}
        self.outputs['I_guess'] = generate_spherical_diffraction(q, amplitude_at_zero, mean_size, fractional_variation)
        self.outputs['q_I_guess'] = logsafe_zip(q, self.outputs['I_guess'])
        self.outputs['good_flag'] = True ## PLACEHOLDER
        self.outputs['detailed_flags'] = {} ## PLACEHOLDER
