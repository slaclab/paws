import numpy as np

from ...Operation import Operation
from ... import optools

class ArrayMirrorHorizontal(Operation):
    """
    Mirror an array across a horizontal plane,
    i.e., exchange indices along axis 0.
    """

    def __init__(self):
        input_names = ['array_in']
        output_names = ['array_out']
        super(ArrayMirrorHorizontal, self).__init__(input_names, output_names)
        self.input_doc['array_in'] = '2d array'
        self.output_doc['array_out'] = 'input array mirrored horizontally'
        self.input_src['array_in'] = optools.wf_input

    def run(self):
        self.outputs['array_out'] = self.inputs['array_in'][::-1,:]


