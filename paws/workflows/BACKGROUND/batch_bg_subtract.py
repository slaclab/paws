import os
from collections import OrderedDict

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.load_packaged_workflow('bg_subtract','BACKGROUND.bg_subtract')
wfmgr.workflows['bg_subtract'].disable_op('read_bg')
wfmgr.add_workflow('batch_bgsub')

wfmgr.load_operations('batch_bgsub',
    read_bg = 'IO.NumpyLoad',
    data_files = 'IO.FILESYSTEM.BuildFileList',
    batch_bgsub = 'EXECUTION.Batch'
    )

wf = wfmgr.workflows['batch_bgsub']

# input: path to background data 
wf.connect_input('bg_file','read_bg.inputs.file_path')
# input: path to directory with data files
wf.connect_input('data_dir','data_files.inputs.dir_path')
# input: regex for data files 
wf.connect_input('data_regex','data_files.inputs.regex')
wf.set_op_input('data_files','regex','*.dat')

wf.connect_workflow('bg_subtract','batch_bgsub.inputs.work_item')
wf.connect('data_files.outputs.file_list','batch_bgsub.inputs.batch_inputs.data_file')
wf.connect('read_bg.outputs.data','batch_bgsub.inputs.static_inputs.bg_data')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','BACKGROUND','batch_bg_subtract.wfm'))

