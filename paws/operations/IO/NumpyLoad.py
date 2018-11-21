from collections import OrderedDict
import os

import numpy as np

from ..Operation import Operation

inputs=OrderedDict(
    file_path=None,
    dtype='float',
    delimiter=' ')

outputs=OrderedDict(
    data=None,
    dir_path=None,
    filename=None) 

class NumpyLoad(Operation):
    """Wrapper for numpy.loadtxt."""

    def __init__(self):
        super(NumpyLoad, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to data file'
        self.input_doc['dtype'] = 'datatype (given as a string)'
        self.input_doc['delimiter'] = 'delimiter (str) placed between values'
        self.output_doc['data'] = 'result of loading file contents'
        self.output_doc['dir_path'] = 'directory of the input file' 
        self.output_doc['filename'] = 'name of the input file, no path, no extension' 
        self.output_doc['extension'] = 'extension of the input file path' 

    def run(self):
        p = self.inputs['file_path']
        self.message_callback('reading {}'.format(p))
        dlm = self.inputs['delimiter']
        dtp = eval(self.inputs['dtype']) 
        self.outputs['dir_path'], fn = os.path.split(p)
        self.outputs['filename'], self.outputs['extension'] = os.path.splitext(fn) 
        self.outputs['data'] = np.loadtxt(p, dtype=dtp, delimiter=dlm)
        return self.outputs

