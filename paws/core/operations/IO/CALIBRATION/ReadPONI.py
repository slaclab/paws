from collections import OrderedDict

from ... import Operation as op
from ...Operation import Operation

class ReadPONI(Operation):
    """
    Read in a dict of PyFAI PONI parameters.
    Input path to a .poni file representing a calibrated measurement geometry.
    """
    
    def __init__(self):
        input_names = ['poni_file']
        output_names = ['poni_dict']
        super(ReadPONI,self).__init__(input_names,output_names)
        self.input_doc['poni_file'] = '.poni file describing a calibration result'
        self.input_src['poni_file'] = op.fs_input
        self.input_type['poni_file'] = op.path_type
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters, as found in a .poni file'

    def run(self):
        fpath = self.inputs['poni_file']
        pdict = OrderedDict()
        for line in open(fpath,'r'):
            kv = line.strip().split('=')
            if kv[0] == 'dist':
                pdict['dist'] = float(kv[1])         
            if kv[0] == 'poni1':
                pdict['poni1'] = float(kv[1])       
            if kv[0] == 'poni2':
                pdict['poni2'] = float(kv[1])       
            if kv[0] == 'rot1':    
                pdict['rot1'] = float(kv[1])       
            if kv[0] == 'rot2':    
                pdict['rot2'] = float(kv[1])       
            if kv[0] == 'rot3':    
                pdict['rot3'] = float(kv[1])       
            if kv[0] == 'pixel1':    
                pdict['pixel1'] = float(kv[1])       
            if kv[0] == 'pixel2':    
                pdict['pixel2'] = float(kv[1])       
            if kv[0] == 'wavelength':    
                pdict['wavelength'] = float(kv[1])       
            if kv[0] == 'fpolz':    
                pdict['fpolz'] = float(kv[1])       
            if kv[0] == 'detector':    
                pdict['detector'] = kv[1]
            if kv[0] == 'splineFile':    
                pdict['splineFile'] = kv[1]
        self.outputs['poni_dict'] = pdict 

