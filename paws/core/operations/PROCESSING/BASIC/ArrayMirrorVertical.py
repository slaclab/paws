import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

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

    def run(self):
        x = self.inputs['array_in']
        if x is None:
            return
        self.outputs['array_out'] = x[:,::-1]


