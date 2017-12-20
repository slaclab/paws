from collections import OrderedDict

import pyFAI

from ...Operation import Operation
from ... import Operation as opmod 

inputs=OrderedDict(
    dark_img=None,
    flat_img=None,
    mask_img=None,
    polz_factor=0.)
outputs=OrderedDict(pyfai_args=None)

class GetPyFAIArgs(Operation):
    """Set up a dict of keyword args for a PyFAI.AzimuthalIntegrator."""
    
    def __init__(self):
        super(GetPyFAIArgs,self).__init__(inputs,outputs)
        self.input_doc['dark_img'] = 'image data for dark field'
        self.input_doc['flat_img'] = 'image data for dark field'
        self.input_doc['mask_img'] = 'image data for mask'
        self.input_doc['polz_factor'] = 'polarization factor'
        self.output_doc['poni_dict'] = 'Dict of pyFAI calibration parameters'

    def run(self):
        pdict = dict(
            mask = self.inputs['mask_img'],
            dark = self.inputs['dark_img'],
            flat = self.inputs['flat_img'],
            polarization_factor = self.inputs['polz_factor'])
        self.outputs['pyfai_args'] = pdict 

