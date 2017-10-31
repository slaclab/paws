import os
from collections import OrderedDict

import numpy as np
import pyFAI

from .. import Operation as opmod 
from ..Operation import Operation

inputs=OrderedDict(poni_file=None)
outputs=OrderedDict(poni_dict=None)

class ReadPONI(Operation):
    """
    Reads in a .poni file as output by 
    pyFAI.geometry.Geometry.save(),
    outputs a poni dict
    as produced by pyFAI.geometry.Geometry.getPyFAI().
    """
    
    def __init__(self):
        super(ReadPONI,self).__init__(inputs,outputs)
        self.input_doc['poni_file'] = 'path to the .poni file' 
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters'

    def run(self):
        fpath = self.inputs['poni_file']
        g = pyFAI.geometry.Geometry()
        g.read(fpath)
        self.outputs['poni_dict'] = g.getPyFAI() 

