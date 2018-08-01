import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.load_packaged_workflow('read','IO.BL15.read')
wfmgr.add_workflow('batch_read')
wfmgr.load_operations('batch_read',
    header_files='IO.FILESYSTEM.BuildFileList',
    batch='EXECUTION.Batch'
    )

wf = wfmgr.workflows['batch_read']

wf.connect_workflow('read','batch.inputs.work_item')
# input: header file path
wf.connect_input('header_dir','header_files.inputs.dir_path') 
# input: header files regex 
wf.connect_input('header_regex','header_files.inputs.regex') 
wf.connect_input('q_I_suffix','batch.inputs.static_inputs.q_I_suffix') 
wf.connect_input('populations_dir','batch.inputs.static_inputs.populations_dir') 
wf.connect_input('populations_suffix','batch.inputs.static_inputs.populations_suffix') 
wf.connect_input('q_I_ext','batch.inputs.static_inputs.q_I_ext')
wf.connect_input('image_dir','batch.inputs.static_inputs.image_dir')
wf.connect_input('q_I_dir','batch.inputs.static_inputs.q_I_dir')
wf.connect_output('batch_outputs','batch.outputs.batch_outputs')
wf.connect('header_files.outputs.file_list','batch.inputs.batch_inputs.header_file')

wf.connect_output('header_files','batch.outputs.batch_outputs.header_file')
wf.connect_output('image_files','batch.outputs.batch_outputs.image_file')
wf.connect_output('q_I_files','batch.outputs.batch_outputs.q_I_file')
wf.connect_output('header_data','batch.outputs.batch_outputs.header_data')
wf.connect_output('image_data','batch.outputs.batch_outputs.image_data')
wf.connect_output('q_I_data','batch.outputs.batch_outputs.q_I_data')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','IO','BL15','batch_read.wfm'))

