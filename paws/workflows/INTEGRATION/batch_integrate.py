import os
from collections import OrderedDict

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.load_packaged_wfm('INTEGRATION.integrate')
wfmgr.add_workflow('batch_integrate')

wfmgr.load_operations('batch_integrate',
    image_files = 'IO.FILESYSTEM.BuildFileList',
    batch_integrate = 'EXECUTION.Batch'
    )

wf = wfmgr.workflows['batch_integrate']

wf.connect_input('image_dir','image_files.inputs.dir_path')
wf.set_op_input('image_files','regex','*.tif')
wf.connect_input('image_regex','image_files.inputs.regex')

wf.connect_workflow('integrate','batch_integrate.inputs.work_item')
wf.connect_input('q_min','batch_integrate.inputs.static_inputs.q_min')
wf.connect_input('q_max','batch_integrate.inputs.static_inputs.q_max')
wf.connect_input('output_dir','batch_integrate.inputs.static_inputs.output_dir')
wf.connect_input('filename','batch_integrate.inputs.static_inputs.filename')
wf.connect('image_files.outputs.file_list','batch_integrate.inputs.batch_inputs.image_file')
#wf.connect('image_files.inputs.dir_path','batch_integrate.inputs.static_inputs.dir_path')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','batch_integrate.wfm'))

