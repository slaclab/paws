import numpy as np
from collections import OrderedDict

from ...Operation import Operation

inputs=OrderedDict(array_in=None)
outputs=OrderedDict(array_out=None)

class ArrayMirrorHorizontal(Operation):
    """Mirror an array across a horizontal plane.

    Exchanges indices along axis 0.
    """

    def __init__(self):
        super(ArrayMirrorHorizontal, self).__init__(inputs, outputs)
        self.input_doc['array_in'] = '2d array'
        self.output_doc['array_out'] = 'input array mirrored horizontally'

    def run(self):
        x = self.inputs['array_in']
        self.outputs['array_out'] = np.array(x[::-1,:])

