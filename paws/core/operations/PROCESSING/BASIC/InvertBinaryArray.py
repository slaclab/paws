import numpy as np
from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation

inputs = OrderedDict(x=None)
outputs = OrderedDict(invx=None)

class InvertBinaryArray(Operation):
    """Swap the zeros and ones of a binary array."""

    def __init__(self):
        super(InvertBinaryArray, self).__init__(inputs, outputs)
        self.input_doc['x'] = 'binary array (ones and zeros, or booleans)'
        self.output_doc['invx'] = 'the binary inverse of x'

    def run(self):
        x = np.array(self.inputs['x'],dtype=bool)
        self.outputs['invx'] = np.array(np.invert(x))

