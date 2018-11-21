from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(
    marccd_client=None,
    exposure_time=10.,
    filename=None)
outputs=OrderedDict()
        
class MarCCDExpose(Operation):
    """Trigger a running MarCCDClient Plugin to take an exposure"""

    def __init__(self):
        super(MarCCDExpose,self).__init__(inputs,outputs)
        self.input_doc['marccd_client'] = 'A MarCCDClient Plugin'
        self.input_doc['exposure_time'] = 'The exposure time in seconds' 
        self.input_doc['filename'] = 'Filename to save the image' 

    def run(self):
        cl = self.inputs['marccd_client'] 
        t_exp = self.inputs['exposure_time'] 
        fn = self.inputs['filename']
        cl.request_exposure(t_exp,fn)

