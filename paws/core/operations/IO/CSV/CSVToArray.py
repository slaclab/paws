import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

class CSVToArray(Operation):
    """
    Read a csv-formatted file into a numpy array.
    """

    def __init__(self):
        input_names = ['path']
        output_names = ['array']
        super(CSVToArray, self).__init__(input_names, output_names)
        self.input_doc['path'] = "path to .csv file"
        self.output_doc['array'] = "numpy array built from csv file contents"

    def run(self):
        path = self.inputs['path']
        if path is None:
            return
        self.outputs['array'] = np.loadtxt(path, dtype=float, delimiter=',')


