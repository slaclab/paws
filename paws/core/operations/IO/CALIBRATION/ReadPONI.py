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
        input_names = ['poni_file','fpolz']
        output_names = ['poni_dict']
        super(ReadPONI,self).__init__(input_names,output_names)
        self.input_doc['poni_file'] = '.poni file describing a calibration result'
        self.input_doc['fpolz'] = 'polarization factor, to be added into the dict. Default value is 1.'
        self.input_type['poni_file'] = opmod.filesystem_path
        self.input_type['fpolz'] = opmod.float_type
        self.inputs['fpolz'] = float(1.) 
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters, as found in a .poni file'

    def run(self):
        fpath = self.inputs['poni_file']
        fpolz = self.inputs['fpolz']
        g = pyFAI.geometry.Geometry()
        g.read(fpath)
        pdict = g.getPyFAI()
        pdict['fpolz'] = fpolz
        self.outputs['poni_dict'] = pdict 

