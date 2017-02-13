import numpy as np

from ..slacxop import Operation
from .. import optools

class WindowByWavelength(Operation):
    """Window a spectrum to user-selected wavelengths."""

    def __init__(self):
        input_names = ['q', 'I', 'q1', 'q2', 'zip', 'log_zip']
        output_names = ['q', 'I', 'q_I', 'log_q_log_I']
        super(WindowByWavelength, self).__init__(input_names, output_names)
        self.input_doc['q'] = 'wavelength'
        self.input_doc['I'] = 'intensity'
        self.input_doc['q1'] = 'lower bound of region of interest'
        self.input_doc['q2'] = 'upper bound of region of interest'
        self.input_doc['zip'] = 'would you like zipped results?'
        self.input_doc['log_zip'] = 'would you like log-zipped results?'
        self.output_doc['q'] = 'windowed q'
        self.output_doc['I'] = 'windowed I'
        self.output_doc['q_I'] = 'windowed, zipped q and I, if requested'
        self.output_doc['log_q_log_I'] = 'windowed, zipped log q and log I, if requested'
        # source & type
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['q1'] = optools.text_input
        self.input_src['q2'] = optools.text_input
        self.input_src['zip'] = optools.text_input
        self.input_src['log_zip'] = optools.text_input
        self.input_type['q1'] = optools.float_type
        self.input_type['q2'] = optools.float_type
        self.input_type['zip'] = optools.bool_type
        self.input_type['log_zip'] = optools.bool_type
        # defaults
        self.inputs['q1'] = 0.02
        self.inputs['q2'] = 0.7
        self.inputs['zip'] = False
        self.inputs['log_zip'] = True
        self.categories = ['PROCESSING']

    def run(self):
        self.outputs['sum'] = self.inputs['augend'] + self.inputs['addend']


class WindowByIntensity(Operation):
    """Window a spectrum by allowing only credible values of intensity.

    Optionally, a few pixels to each side of the invalid region can be ignored."""

    def __init__(self):
        input_names = ['q', 'I', 'I_min', 'I_max', 'pad', 'zip', 'log_zip']
        output_names = ['q', 'I', 'q_I', 'log_q_log_I']
        super(WindowByIntensity, self).__init__(input_names, output_names)
        self.input_doc['q'] = 'wavelength'
        self.input_doc['I'] = 'intensity'
        self.input_doc['I_min'] = 'lowest credible value of I'
        self.input_doc['I_max'] = 'highest credible value of I'
        self.input_doc['pad'] = 'additional pixels to either side of invalid region excluded'
        self.input_doc['zip'] = 'would you like zipped results?'
        self.input_doc['log_zip'] = 'would you like log-zipped results?'
        self.output_doc['q'] = 'windowed q'
        self.output_doc['I'] = 'windowed I'
        self.output_doc['q_I'] = 'windowed, zipped q and I, if requested'
        self.output_doc['log_q_log_I'] = 'windowed, zipped log q and log I, if requested'
        # source & type
        self.input_src[''] = optools.wf_input
        self.input_type[''] = optools.float_type
        # defaults
        self.inputs['I_min'] = 0.0
        self.inputs['I_max'] = None
        self.inputs['pad'] = 1
        self.inputs['zip'] = False
        self.inputs['log_zip'] = True

        self.categories = ['PROCESSING']

    def run(self):
        self.outputs['sum'] = self.inputs['augend'] + self.inputs['addend']

