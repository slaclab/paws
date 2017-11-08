import numpy as np
from collections import OrderedDict

from ...Operation import Operation

inputs=OrderedDict(array_in=None)
outputs=OrderedDict(array_out=None)

class ArrayMirrorVertical(Operation):
    """Mirror an array across a vertical plane.
    
    Exchanges indices along axis 1.
    """

    def __init__(self):
        super(ArrayMirrorVertical, self).__init__(inputs, outputs)
        self.input_doc['array_in'] = '2d array'
        self.output_doc['array_out'] = 'input array mirrored vertically'

    def run(self):
        x = self.inputs['array_in']
        self.outputs['array_out'] = x[:,::-1]


