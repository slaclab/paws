from collections import OrderedDict

import pyFAI

from ..Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(poni_dict=None)

class ReadPONI(Operation):
    """
    Read in a dict of PyFAI PONI parameters.
    Input path to a .poni file representing a calibrated measurement geometry.
    """
    
    def __init__(self):
        super(ReadPONI,self).__init__(inputs,outputs)
        self.input_doc['file_path'] = 'Path to a .poni file '\
            'describing a calibrated sample-detector geometry'
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters'

    def run(self):
        fpath = self.inputs['file_path']
        g = pyFAI.geometry.Geometry()
        g.read(fpath)
        pdict = g.getPyFAI()
        self.outputs['poni_dict'] = pdict 

