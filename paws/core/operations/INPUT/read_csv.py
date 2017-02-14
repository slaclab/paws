import numpy as np

from ..operation import Operation
from ..import optools


class ReadCSV_q_I_dI(Operation):
    """Read q, I, and (if available) dI from a csv-formatted file.

    If the csv has no third column, returns None for dI."""

    def __init__(self):
        input_names = ['csv_location']
        output_names = ['q','I', 'dI']
        super(ReadCSV_q_I_dI, self).__init__(input_names, output_names)
        # docstrings
        self.output_doc['q'] = "1d ndarray; independent variable"
        self.output_doc['I'] = "1d ndarray; dependent variable; same shape as *q*"
        self.output_doc['dI'] = "1d ndarray; error estimate of *I*; same shape as *I*"
        # source & type
        self.input_src['csv_location'] = optools.fs_input
        self.input_type['csv_location'] = optools.str_type
        self.categories = ['INPUT.CSV']

    def run(self):
        csv_location = self.inputs['csv_location']
        q, I, dI = read_csv_q_I_maybe_dI(csv_location)
        self.outputs['q'] = q
        self.outputs['I'] = I
        self.outputs['dI'] = dI

def read_csv_q_I_maybe_dI(nameloc):
    q = np.loadtxt(nameloc, dtype=float, delimiter=',', skiprows=1, usecols=(0,))
    I = np.loadtxt(nameloc, dtype=float, delimiter=',', skiprows=1, usecols=(1,))
    try:
        dI = np.loadtxt(nameloc, dtype=float, delimiter=',', skiprows=1, usecols=(2,))
    except IndexError:
        dI = None
    return q, I, dI

