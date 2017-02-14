from os.path import splitext
from os import linesep
import numpy as np

from ..operation import Operation
from ..import optools

class WriteArrayCSV(Operation):
    """Write a 2d array to a csv file"""

    def __init__(self):
        input_names = ['array','headers','filepath','filename','filetag']
        output_names = ['csv_path']
        super(WriteArrayCSV, self).__init__(input_names, output_names)
        self.input_doc['array'] = 'any 2d array'
        self.input_doc['headers'] = 'list of headers- should be one for each column of array'
        self.input_doc['filepath'] = 'the path to the destination directory'
        self.input_doc['filename'] = 'the name of the file to be saved- the .csv extension will be added/replaced if not provided'
        self.output_doc['csv_path'] = 'the path to the finished csv file'
        self.input_src['array'] = optools.wf_input
        self.input_src['headers'] = optools.text_input
        self.input_src['filepath'] = optools.fs_input
        self.input_src['filename'] = optools.text_input
        self.input_type['array'] = optools.ref_type
        self.input_type['headers'] = optools.str_type
        self.input_type['filepath'] = optools.str_type
        self.input_type['filename'] = optools.str_type

    def run(self):
        h = self.inputs['headers']
        a = self.inputs['array']
        csv_path = splitext(self.inputs['filepath']+self.inputs['filename'])[0]+'.csv'
        self.outputs['csv_path'] = csv_path
        h_str = ''
        for i in range(len(h)-1):
            h_str += h[i] + ', '
        h_str = h_str+h[-1]
        np.savetxt(csv_path, a, delimiter=',', newline=linesep, header=h_str)

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
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['dI'] = optools.wf_input
        self.input_src['image_location'] = optools.wf_input
        self.categories = ['OUTPUT.CSV']

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

