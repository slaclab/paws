import numpy as np

from ...Operation import Operation
from ... import optools

class ArrayMirrorVertical(Operation):
    """
    Mirror an array across a vertical plane,
    i.e., exchange indices along axis 1.
    """

    def __init__(self):
        input_names = ['array_in']
        output_names = ['array_out']
        super(ArrayMirrorVertical, self).__init__(input_names, output_names)
        self.input_doc['array_in'] = '2d array'
        self.output_doc['array_out'] = 'input array mirrored vertically'
        self.input_src['array_in'] = optools.wf_input

    def run(self):
        self.outputs['array_out'] = self.inputs['array_in'][:,::-1]


