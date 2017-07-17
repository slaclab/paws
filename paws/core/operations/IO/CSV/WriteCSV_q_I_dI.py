from os.path import splitext
from os import linesep
import numpy as np

from ... import Operation as op
from ...Operation import Operation

class WriteCSV_q_I_dI(Operation):
    """Write q, I, and (if available) dI to a csv-formatted file."""

    def __init__(self):
        input_names = ['q','I','dI','image_location']
        output_names = ['csv_location']
        super(WriteCSV_q_I_dI, self).__init__(input_names, output_names)
        # docstrings
        self.input_doc['q'] = "1d ndarray; independent variable"
        self.input_doc['I'] = "1d ndarray; dependent variable; same shape as *q*"
        self.input_doc['dI'] = "1d ndarray; error estimate of *I*; same shape as *I*; if unavailable, use *None*"
        # source & type
        self.input_src['q'] = op.wf_input
        self.input_src['I'] = op.wf_input
        self.input_src['dI'] = op.wf_input
        self.input_src['image_location'] = op.wf_input

    def run(self):
        csv_location = replace_extension(self.inputs['image_location'], '.csv')
        write_csv_q_I_maybe_dI(self.inputs['q'], self.inputs['I'], self.inputs['dI'], csv_location)
        self.outputs['csv_location'] = csv_location


def write_csv_q_I_maybe_dI(q, I, dI, nameloc):
    if dI is None:
        datablock = np.zeros((q.size,2),dtype=float)
        top_line = 'q, I'
    else:
        datablock = np.zeros((q.size,3),dtype=float)
        datablock[:,2] = dI
        top_line = 'q, I, dI'
    datablock[:,0] = q
    datablock[:,1] = I
    np.savetxt(nameloc, datablock, delimiter=',', newline=linesep, header=top_line)


def replace_extension(old_name, new_extension):
    '''
    Return a file name that is identical except for extension.

    :param old_name: string path or file name
    :param new_extension: string extension, e.g. ".txt"
    :return:

    Accepts extensions with or without an initial ".".
    '''
    # os.splitext gives the extension with '.' in front.
    # Rather than require the user to know this, I take care of it here.
    if new_extension[0] != '.':
        new_extension = '.' + new_extension
    root = splitext(old_name)[0]
    new_name = root + new_extension
    return new_name

