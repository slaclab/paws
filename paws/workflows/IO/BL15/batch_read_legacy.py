import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_workflow('read','IO.BL15.read')
wfmgr.add_workflow('batch_read')
wfmgr.load_operations('batch_read',
    header_files='IO.FILESYSTEM.BuildFileList',
    batch='EXECUTION.Batch',
    )

wf = wfmgr.workflows['batch_read']

# input: header file path
wf.connect_input('header_dir','header_files.inputs.dir_path') 
# input: header files regex 
wf.connect_input('header_regex','header_files.inputs.regex') 
wf.connect_output('batch_outputs','batch_read.outputs.batch_outputs')
wf.connect('header_files.outputs.file_list','batch.inputs.batch_inputs.header_filepath')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15','batch_read_legacy.wfm'))

