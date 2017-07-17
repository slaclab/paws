import numpy as np

from ... import Operation as op
from ...Operation import Operation

class ReadCSV_q_I_dI(Operation):
    """
    Read q, I, and (if available) dI from a csv-formatted file.
    If the csv has no third column, returns None for dI.
    """

    def __init__(self):
        input_names = ['path']
        output_names = ['q','I', 'dI']
        super(ReadCSV_q_I_dI, self).__init__(input_names, output_names)
        self.input_doc['path'] = "path to .csv file"
        self.output_doc['q'] = "1d array, first column of csv, presumed to be scattering vector q"
        self.output_doc['I'] = "1d array, second column of csv, presumed to be scattering intensity I"
        self.output_doc['dI'] = "1d array, third column of csv, presumed to be error estimate of I"
        # source & type
        self.input_src['path'] = op.fs_input
        self.input_type['path'] = op.path_type

    def run(self):
        path = self.inputs['path']
        ncols = np.loadtxt(path, delimiter=',', skiprows=1).shape[1]
        if ncols == 2:
            q, I = np.loadtxt(path, dtype=float, delimiter=',', unpack=True, skiprows=1)
            dI = None
        elif ncols == 3:
            q, I, dI = np.loadtxt(path, dtype=float, delimiter=',', unpack=True, skiprows=1)
        #elif ncols == 4:
        #    col1, col2, col3, col4 = np.loadtxt(path, dtype=float, delimiter=',', unpack=True)
        else:
            raise ValueError("Input file has the wrong number of columns.  I don't know what to do with this.")
        self.outputs['q'] = q
        self.outputs['I'] = I
        self.outputs['dI'] = dI


