from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(
    file_path=None,
    delimiter=None)
outputs=OrderedDict(array=None)

class CSVToArray(Operation):
    """
    Read a csv-formatted file into a numpy array.
    """

    def __init__(self):
        super(CSVToArray, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = "path to .csv file"
        self.output_doc['array'] = "numpy array built from csv file contents"

    def run(self):
        p = self.inputs['file_path']
        self.outputs['array'] = np.loadtxt(p, dtype=float, delimiter=',')


