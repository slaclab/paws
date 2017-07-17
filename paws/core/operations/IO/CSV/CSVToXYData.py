import numpy as np

from ... import Operation as op
from ...Operation import Operation

class CSVToXYData(Operation):
    """
    Read a csv-formatted file into x values and y values.
    """

    def __init__(self):
        input_names = ['path']
        output_names = ['x','y','x_y']
        super(CSVToXYData, self).__init__(input_names, output_names)
        self.input_doc['path'] = 'path to .csv file'
        self.output_doc['x'] = 'numpy array built from first column of csv data'
        self.output_doc['y'] = 'numpy array built from second column of csv data'
        self.output_doc['x_y'] = 'n-by-2 numpy array with x and y values'
        # source & type
        self.input_src['path'] = op.fs_input
        self.input_type['path'] = op.path_type

    def run(self):
        path = self.inputs['path']
        x = np.loadtxt(path, dtype=float, delimiter=',', usecols=[0])
        y = np.loadtxt(path, dtype=float, delimiter=',', usecols=[1])
        self.outputs['x'] = x
        self.outputs['y'] = y
        x_y = np.array([x,y]).T
        self.outputs['x_y'] = x_y 
        


