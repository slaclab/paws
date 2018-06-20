import os
from collections import OrderedDict

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.load_packaged_wfm('INTEGRATION.BL15.integrate')
wfmgr.add_workflow('main')

wfmgr.load_operations('main',
    header_files = 'IO.FILESYSTEM.BuildFileList',
    batch_integrate = 'EXECUTION.Batch'
    )

wf = wfmgr.workflows['main']

# input: path to directory with header files
wf.connect_input('header_dir','header_files.inputs.dir_path')

# input: regex for header files 
wf.set_op_input('header_files','regex','*.txt')
wf.connect_input('header_regex','header_files.inputs.regex')

wf.connect_workflow('integrate','batch_integrate.inputs.work_item')
wf.connect('header_files.outputs.file_list','batch_integrate.inputs.batch_inputs.header_file')
wf.connect_plugin('integrator','batch_integrate.inputs.static_inputs.integrator')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','INTEGRATION','BL15','batch_integrate.wfm'))

