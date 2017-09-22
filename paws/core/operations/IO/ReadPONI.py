import os

import numpy as np
import pyFAI

from .. import Operation as opmod 
from ..Operation import Operation

class ReadPONI(Operation):
    """
    Reads in a .poni file as output by 
    pyFAI.geometry.Geometry.save(),
    outputs a poni dict
    as produced by pyFAI.geometry.Geometry.getPyFAI().
    """
    
    def __init__(self):
        input_names = ['poni_file']
        output_names = ['poni_dict']
        super(ReadPONI,self).__init__(input_names,output_names)
        self.input_doc['poni_file'] = 'path to the .poni file' 
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters'

    def run(self):
        fpath = self.inputs['poni_file']
        if fpath is None:
            return
        g = pyFAI.geometry.Geometry()
        g.read(fpath)
        self.outputs['poni_dict'] = g.getPyFAI() 

