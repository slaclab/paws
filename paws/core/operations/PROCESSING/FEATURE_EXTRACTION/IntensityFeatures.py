"""
Created on Mon Jun 06 18:02:32 2016

author(s): Fang Ren, Apurva Mehta
Module originally contributed by Fang Ren.
For details, refer to the recent paper submitted to ACS Combinatorial Science.
TODO: Get this citation
"""

import numpy as np

from ... import Operation as op
from ...Operation import Operation

class IntensityFeatures(Operation):
    """
    Extract the maximum intensity, average intensity, and a ratio of the two from data
    """

    def __init__(self):
        input_names = ['I']
        output_names = ['Imax', 'Iave', 'Imax_Iave_ratio']
        super(IntensityFeatures, self).__init__(input_names, output_names)
        self.input_doc['I'] = 'A 1d vector representing the intensity spectrum'
        self.input_src['I'] = op.wf_input
        self.output_doc['Imax'] = 'The maximum intensity '
        self.output_doc['Iave'] = 'The average intensity'
        self.output_doc['Imax_Iave_ratio'] = 'The ratio of maximum to average intensity'

    def run(self):
        Imax = np.max(self.inputs['I'])
        Iave = np.mean(self.inputs['I'])
        ratio = Imax/Iave
        self.outputs['Imax'] = Imax
        self.outputs['Iave'] = Iave
        self.outputs['Imax_Iave_ratio'] = ratio

