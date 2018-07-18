import os

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()

wfmgr.load_packaged_workflow('bg_read','IO.BL15.read_legacy')
wfmgr.workflows['bg_read'].disable_ops('read_image','read_q_I')
wfmgr.load_packaged_workflow('sample_read','IO.BL15.read_legacy')
wfmgr.workflows['sample_read'].disable_ops('read_image','read_q_I')
wfmgr.load_packaged_workflow('bg_subtract','BACKGROUND.bg_subtract')
wfmgr.add_workflow('main')
wfmgr.load_operations('main',
    bg_header_files = 'IO.FILESYSTEM.BuildFileList',
    sample_header_files = 'IO.FILESYSTEM.BuildFileList',
    batch_bg_read = 'EXECUTION.Batch',
    batch_sample_read = 'EXECUTION.Batch',
    choose_bg_file = 'PACKAGING.NearestYValue',
    choose_bg_files = 'EXECUTION.Batch',
    batch_bgsub = 'EXECUTION.Batch'
    )

wf = wfmgr.workflows['main']

wf.connect_input('bg_header_dir','bg_header_files.inputs.dir_path')
wf.set_op_input('bg_header_files','regex','*.txt')

wf.connect_input('sample_header_dir','sample_header_files.inputs.dir_path')
wf.set_op_input('sample_header_files','regex','*.txt')

wf.connect_input('time_key',[
    'batch_bg_read.inputs.static_inputs.time_key',
    'batch_sample_read.inputs.static_inputs.time_key']
    )
wf.connect_input('temperature_key',[
    'batch_bg_read.inputs.static_inputs.temperature_key',
    'batch_sample_read.inputs.static_inputs.temperature_key']
    )

wf.connect_input('bg_q_I_dir','batch_bg_read.inputs.static_inputs.q_I_dir')
wf.connect_input('bg_q_I_suffix','batch_bg_read.inputs.static_inputs.q_I_suffix')
wf.connect_workflow('bg_read','batch_bg_read.inputs.work_item')
wf.connect('bg_header_files.outputs.file_list','batch_bg_read.inputs.batch_inputs.header_file')

wf.connect_input('sample_q_I_dir','batch_sample_read.inputs.static_inputs.q_I_dir')
wf.connect_input('sample_q_I_suffix','batch_sample_read.inputs.static_inputs.q_I_suffix')
wf.connect_workflow('sample_read','batch_sample_read.inputs.work_item')
wf.connect('sample_header_files.outputs.file_list','batch_sample_read.inputs.batch_inputs.header_file')

wf.disable_op('choose_bg_file')
wf.connect('choose_bg_file','choose_bg_files.inputs.work_item')
wf.connect('batch_sample_read.outputs.batch_outputs.temperature','choose_bg_files.inputs.batch_inputs.x_value')
wf.connect('batch_bg_read.outputs.batch_outputs.temperature','choose_bg_files.inputs.static_inputs.x')
wf.connect('batch_bg_read.outputs.batch_outputs.q_I_file','choose_bg_files.inputs.static_inputs.y')

wf.connect_workflow('bg_subtract','batch_bgsub.inputs.work_item')
wf.connect('batch_sample_read.outputs.batch_outputs.q_I_file','batch_bgsub.inputs.batch_inputs.q_I_file')
wf.connect('choose_bg_files.outputs.batch_outputs.nearest_y','batch_bgsub.inputs.batch_inputs.q_I_bg_file')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','BACKGROUND','batch_T_dependent_bgsub.wfm'))

