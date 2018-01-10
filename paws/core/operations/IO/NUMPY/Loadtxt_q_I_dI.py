from collections import OrderedDict
import os

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(
    file_path=None,
    delimiter=None)
outputs=OrderedDict(
    q=None,
    I=None,
    q_I=None,
    dI=None,
    dir_path=None,
    filename=None) 

class Loadtxt_q_I_dI(Operation):
    """Read in q, I, and (optionally) error estimate dI, with numpy.loadtxt."""

    def __init__(self):
        super(Loadtxt_q_I_dI, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to data file'
        self.input_doc['delimiter'] = 'delimiter used in data file (optional)'
        self.output_doc['filename'] = 'filename with path and extension stripped'
        self.output_doc['q'] = 'array of q values' 
        self.output_doc['I'] = 'array of intensities' 
        self.output_doc['q_I'] = 'n-by-2 array of q and intensity' 
        self.output_doc['dI'] = 'array of intensity error estimates' 
        self.input_datatype['file_path'] = 'str'
        self.input_datatype['delimiter'] = 'str'

    def run(self):
        p = self.inputs['file_path']
        dlm = self.inputs['delimiter']

        self.outputs['dir_path'] = os.path.split(p)[0]
        filename = os.path.split(p)[1]
        filename_noext = os.path.splitext(filename)[0]
        self.outputs['filename'] = filename_noext 

        d = np.loadtxt(p, delimiter=dlm)
        self.outputs['q'] = d[:,0]
        self.outputs['I'] = d[:,1]
        self.outputs['q_I'] = d[:,0:2]
        if d.shape[1] > 2:
            self.outputs['dI'] = d[:,2]


