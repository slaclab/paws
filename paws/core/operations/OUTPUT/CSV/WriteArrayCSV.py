from os.path import splitext
from os import linesep
import numpy as np

from ...Operation import Operation
from ... import optools

class WriteArrayCSV(Operation):
    """Write a 2d array to a csv file"""

    def __init__(self):
        input_names = ['array','headers','dirpath','filename','filetag']
        output_names = ['csv_path']
        super(WriteArrayCSV, self).__init__(input_names, output_names)
        self.input_doc['array'] = 'any 2d array'
        self.input_doc['headers'] = 'list of headers (optional)- one header for each column of array'
        self.input_doc['dirpath'] = 'the path to the destination directory'
        self.input_doc['filename'] = 'the name of the file to be saved- .csv will be appended if not provided'
        self.input_doc['filetag'] = 'tag appended to filename'
        self.output_doc['csv_path'] = 'the path to the finished csv file'
        self.input_src['array'] = optools.wf_input
        self.input_src['headers'] = optools.text_input
        self.input_src['dirpath'] = optools.fs_input
        self.input_src['filename'] = optools.wf_input
        self.input_src['filetag'] = optools.text_input
        self.input_type['array'] = optools.ref_type
        self.input_type['headers'] = optools.str_type
        self.input_type['dirpath'] = optools.path_type
        self.input_type['filename'] = optools.ref_type
        self.input_type['filetag'] = optools.str_type
        self.inputs['filetag'] = ''

    def run(self):
        #import pdb; pdb.set_trace()
        h = self.inputs['headers']
        a = self.inputs['array']
        tag = ''
        if self.inputs['filetag']:
            tag = self.inputs['filetag']
        csv_path = splitext(self.inputs['dirpath']+'/'+self.inputs['filename'])[0]+tag+'.csv'
        self.outputs['csv_path'] = csv_path
        if h is not None:
            h_str = ''
            for i in range(len(h)-1):
                h_str += h[i] + ', '
            h_str = h_str+h[-1]
            np.savetxt(csv_path, a, delimiter=',', newline=linesep, header=h_str)
        else:
            np.savetxt(csv_path, a, delimiter=',', newline=linesep)

