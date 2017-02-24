from os.path import splitext
from os import linesep
import numpy as np

from ...operation import Operation
from ... import optools

class WriteArrayCSV(Operation):
    """Write a 2d array to a csv file"""

    def __init__(self):
        input_names = ['array','headers','dirpath','filename']
        output_names = ['csv_path']
        super(WriteArrayCSV, self).__init__(input_names, output_names)
        self.input_doc['array'] = 'any 2d array'
        self.input_doc['headers'] = 'list of headers- should be one for each column of array'
        self.input_doc['dirpath'] = 'the path to the destination directory'
        self.input_doc['filename'] = 'the name of the file to be saved- the .csv extension will be added/replaced if not provided'
        self.output_doc['csv_path'] = 'the path to the finished csv file'
        self.input_src['array'] = optools.wf_input
        self.input_src['headers'] = optools.text_input
        self.input_src['dirpath'] = optools.fs_input
        self.input_src['filename'] = optools.text_input
        self.input_type['array'] = optools.ref_type
        self.input_type['headers'] = optools.str_type
        self.input_type['dirpath'] = optools.str_type
        self.input_type['filename'] = optools.str_type

    def run(self):
        h = self.inputs['headers']
        a = self.inputs['array']
        csv_path = splitext(self.inputs['dirpath']+self.inputs['filename'])[0]+'.csv'
        self.outputs['csv_path'] = csv_path
        h_str = ''
        for i in range(len(h)-1):
            h_str += h[i] + ', '
        h_str = h_str+h[-1]
        np.savetxt(csv_path, a, delimiter=',', newline=linesep, header=h_str)

