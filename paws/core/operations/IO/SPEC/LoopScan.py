from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    n_loops=1,
    exposure_time=10.,
    delay_time=10.,
    dir_path=None,
    filename=None,
    flag=True)
outputs=OrderedDict(
    flag=False)
        
class LoopScan(Operation):
    """Run a loop scan through a SpecInfoClient"""

    def __init__(self):
        super(LoopScan,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['n_loops'] = 'Number of exposures to run' 
        self.input_doc['exposure_time'] = 'The exposure time in seconds' 
        self.input_doc['delay_time'] = 'Delay between exposures in seconds' 
        self.input_doc['dir_path'] = 'Path to where images should be saved (on detector PC)' 
        self.input_doc['filename'] = 'Filename root for the images' 
        self.input_doc['flag'] = 'Flag for whether or not to start the scan' 
        self.output_doc['flag'] = 'Flag for whether or not the operation finished'

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        n_loops = self.inputs['n_loops'] 
        t_exp = self.inputs['exposure_time'] 
        t_delay = self.inputs['delay_time'] 
        stat = self.inputs['flag']
        dp = self.inputs['dir_path']
        fn = self.inputs['filename']
        mroot = os.path.join(dp,fn)
        if stat:
            cl.mar_enable()
            cl.run_loopscan(mroot,n_loops,t_exp)
            self.message_callback('LoopScan waiting {} seconds...'.format(t_delay))
            time.sleep(t_delay)
            cl.mar_disable()
            self.outputs['flag'] = True 
        else:
            #self.outputs['report'] = {'STATUS':bool(stat)}
            self.outputs['flag'] = False 



