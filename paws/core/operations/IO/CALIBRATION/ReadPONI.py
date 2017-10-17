from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation

import pyFAI

class ReadPONI(Operation):
    """
    Read in a dict of PyFAI PONI parameters.
    Input path to a .poni file representing a calibrated measurement geometry.
    """
    
    def __init__(self):
        input_names = ['file_path']
        output_names = ['poni_dict']
        super(ReadPONI,self).__init__(input_names,output_names)
        self.input_doc['poni_file'] = 'Path to a .poni file '\
            'describing a calibrated sample-detector geometry'
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters'

    def run(self):
        fpath = self.inputs['file_path']
        g = pyFAI.geometry.Geometry()
        g.read(fpath)
        pdict = g.getPyFAI()
        self.outputs['poni_dict'] = pdict 

