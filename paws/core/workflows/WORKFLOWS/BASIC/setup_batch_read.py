import os

import paws.api
from paws.core import pawstools

paw = paws.api.start()

# Activate all the ops that will be used
paw.activate_op('IO.IMAGE.FabIOOpen')
paw.activate_op('EXECUTION.BATCH.BatchFromDirectory')

# Add workflows and name them
paw.add_wf('read_image')
paw.add_wf('batch_read_image')

### Set up read_image workflow ###
paw.select_wf('read_image')
paw.add_op('read','IO.IMAGE.FabIOOpen')
# The batch executor will load the file path at runtime
paw.set_input('read','file_path',None,'runtime')
# Name workflow inputs and outputs
paw.add_wf_input('file_path','read.inputs.file_path')
paw.add_wf_output('image_data','read.outputs.image_data')

### Set up batch_read_image workflow ###
paw.select_wf('batch_read_image')
# declare workflow inputs and outputs
paw.add_op('batch','EXECUTION.BATCH.BatchFromDirectory')
paw.set_input('batch','workflow','read_image')
paw.set_input('batch','input_name','file_path')
paw.add_wf_input('dir_path','batch.inputs.dir_path')
paw.add_wf_input('regex','batch.inputs.regex')
paw.add_wf_output('image_data','batch.outputs.batch_outputs')

paw.save_to_wfl(os.path.join(os.path.dirname(__file__),'batch_read.wfl'))

