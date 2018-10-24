from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    exposure_time=10.,
    filename=None)
outputs=OrderedDict()
        
class MarCCD_SISExpose(Operation):
    """Trigger SpecInfoServer to collect an image from the Mar PC."""

    def __init__(self):
        super(MarCCD_SISExpose,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient Plugin'
        self.input_doc['exposure_time'] = 'The exposure time in seconds' 
        self.input_doc['filename'] = 'Filename to save the image' 

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        t_exp = self.inputs['exposure_time'] 
        fn = self.inputs['filename']
        cl.mar_expose(fn,t_exp)

