from collections import OrderedDict
import time
import os

from ...Operation import Operation

inputs=OrderedDict(
    spec_infoclient=None,
    n_loops=1,
    exposure_time=10.,
    delay_time=0.,
    dir_path=None,
    filename=None,
    block=False)
outputs=OrderedDict()
        
class LoopScan(Operation):
    """Run a loop scan through a SpecInfoClient"""

    def __init__(self):
        super(LoopScan,self).__init__(inputs,outputs)
        self.input_doc['spec_infoclient'] = 'A SpecInfoClient'
        self.input_doc['n_loops'] = 'Number of exposures to run' 
        self.input_doc['exposure_time'] = 'The exposure time in seconds' 
        self.input_doc['delay_time'] = 'Time to wait after sending loop scan commands' 
        self.input_doc['dir_path'] = 'Path to where images should be saved (on SPEC PC)' 
        self.input_doc['filename'] = 'Filename root for the images' 
        self.input_doc['block'] = 'If True, block until loop scan completes' 

    def run(self):
        cl = self.inputs['spec_infoclient'] 
        n_loops = self.inputs['n_loops'] 
        t_exp = self.inputs['exposure_time'] 
        t_delay = self.inputs['delay_time'] 
        dp = self.inputs['dir_path']
        fn = self.inputs['filename']
        blk = self.inputs['block']
        #mroot = os.path.join(dp,fn)
        mroot = dp+'/'+fn   # assume the SPEC PC is Unix
        cl.mar_enable()
        cl.run_loopscan(mroot,n_loops,t_exp,blk)
        #if t_delay > 0.:
        #    self.message_callback('delaying {} seconds...'.format(t_delay))
        #    time.sleep(t_delay)
        cl.mar_disable()



