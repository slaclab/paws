from collections import OrderedDict
import os

import numpy as np

from ..Operation import Operation

inputs=OrderedDict(
    data=None,
    header='',
    file_path=None,
    delimiter=' ')

outputs=OrderedDict(
    dir_path=None,
    filename=None)

class NumpySave(Operation):
    """Wrapper for numpy.savetxt."""

    def __init__(self):
        super(NumpySave, self).__init__(inputs, outputs)
        self.input_doc['data'] = 'data to save to file'
        self.input_doc['header'] = 'header (string) for the output file'
        self.input_doc['file_path'] = 'path where file will be written'
        self.output_doc['dir_path'] = 'directory of the output file' 
        self.output_doc['filename'] = 'name of the output file' 

    def run(self):
        p = self.inputs['file_path']
        self.message_callback('saving to {}'.format(p))
        dlm = self.inputs['delimiter']
        self.outputs['dir_path'],self.outputs['filename'] = os.path.split(p)
        h = self.inputs['header']
        np.savetxt(p, self.inputs['data'], delimiter=dlm, newline=os.linesep, header=h)

