import os

import paws.api

wfl_name = 'batch_fabio_load'
wf_names = ['fabio_load','batch_fabio_load']

paw = paws.api.start()

# Activate all the ops that will be used
paw.activate_op('IO.IMAGE.FabIOOpen')
paw.activate_op('EXECUTION.BATCH.BatchFromDirectory')

# Add workflows and name them
paw.add_wf(wf_names[0])
paw.add_wf(wf_names[1])

### Set up read_image workflow ###
paw.select_wf(wf_names[0])
paw.add_op('read','IO.IMAGE.FabIOOpen')
# The batch executor will load the file path at runtime
paw.set_input('read','file_path',None,'runtime')
# Name workflow inputs and outputs
paw.add_wf_input('file_path','read.inputs.file_path')
paw.add_wf_output('image_data','read.outputs.image_data')

### Set up batch_read_image workflow ###
paw.select_wf('batch_fabio_load')
# declare workflow inputs and outputs
paw.add_op('batch','EXECUTION.BATCH.BatchFromDirectory')
paw.set_input('batch','workflow',wf_names[0])
paw.set_input('batch','input_name','file_path')
paw.add_wf_input('dir_path','batch.inputs.dir_path')
paw.add_wf_input('regex','batch.inputs.regex')
paw.add_wf_output('images','batch.outputs.batch_outputs')

paw.save_to_wfl(os.path.join(os.path.dirname(__file__),wfl_name+'.wfl'))

def test_setup(testpaw):
    from paws.core import pawstools
    test_data_path = os.path.join(pawstools.rootdir,'tests','test_data','noise')
    testpaw.select_wf(wf_names[1])
    testpaw.set_wf_input('dir_path',test_data_path)
    testpaw.set_wf_input('regex','noise_100x100_*.tif')

def test_run(testpaw):
    import numpy as np
    testpaw.select_wf(wf_names[1])
    testpaw.execute()
    reslist = testpaw.get_wf_output('images')
    res = reslist[0]
    img = res['image_data']
    return [(reslist,list),(res,dict),(img,np.ndarray)]



