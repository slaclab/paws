import os
from collections import OrderedDict

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.load_packaged_wfm('INTEGRATION.BL15.LEGACY.integrate')
wfmgr.add_workflow('batch_integrate')

wfmgr.load_operations('batch_integrate',
    header_files = 'IO.FILESYSTEM.BuildFileList',
    batch_integrate = 'EXECUTION.Batch'
    )

wf = wfmgr.workflows['batch_integrate']

# input: path to directory with header files
wf.connect_input('header_dir','header_files.inputs.dir_path')

# input: regex for header files 
wf.set_op_input('header_files','regex','*.txt')
wf.connect_input('header_regex','header_files.inputs.regex')

wf.connect_input('q_min','batch_integrate.inputs.static_inputs.q_min')
wf.connect_input('q_max','batch_integrate.inputs.static_inputs.q_max')
wf.connect_input('image_dir','batch_integrate.inputs.static_inputs.image_dir')
wf.connect_input('image_ext','batch_integrate.inputs.static_inputs.image_ext')
wf.connect_input('output_dir','batch_integrate.inputs.static_inputs.output_dir')
wf.connect_input('temperature_key','batch_integrate.inputs.static_inputs.temperature_key')

wf.connect_workflow('integrate','batch_integrate.inputs.work_item')
wf.connect('header_files.outputs.file_list','batch_integrate.inputs.batch_inputs.header_file')
#wf.connect_plugin('integrator','batch_integrate.inputs.static_inputs.integrator')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','BL15','LEGACY','batch_integrate.wfm'))

