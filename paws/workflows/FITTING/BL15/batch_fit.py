import os

from paws import pawstools
from paws.workflows.WfManager import WfManager

# TODO: refactor to use batch_read

wfmgr = WfManager()
wfmgr.add_workflow('batch_fit')
wfmgr.load_operations('batch_fit',
    header_files='IO.FILESYSTEM.BuildFileList',
    batch_read='EXECUTION.Batch',
    t_system_files='PACKAGING.BATCH.XYDataFromBatch',
    t_q_I_files='PACKAGING.BATCH.XYDataFromBatch',
    t_filenames='PACKAGING.BATCH.XYDataFromBatch',
    run_fits='EXECUTION.Batch'
    )

wfmgr.load_packaged_workflow('read','IO.BL15.read')
wfmgr.load_packaged_workflow('read_and_fit','FITTING.BL15.read_and_fit')
read_wf = wfmgr.workflows['read']
read_wf.disable_op('read_image')
read_wf.disable_op('read_q_I')

wf = wfmgr.workflows['batch_fit']

# input: header files location and regex
wf.connect_input('header_dir','header_files.inputs.dir_path') 
wf.connect_input('header_regex','header_files.inputs.regex') 
# inputs: directories for finding image and data files 
wf.connect_input('image_dir','batch_read.inputs.static_inputs.image_dir')
wf.connect_input('q_I_dir','batch_read.inputs.static_inputs.q_I_dir')
wf.connect_input('q_I_suffix','batch_read.inputs.static_inputs.q_I_suffix')
wf.connect_input('system_dir','batch_read.inputs.static_inputs.system_dir') 
wf.connect_input('system_suffix','batch_read.inputs.static_inputs.system_suffix')
#wf.connect_input('image_dir','batch_read.inputs.static_inputs.image_dir') 
# inputs: initial conditions, bounds, constraints, for fitting
wf.connect_input('source_wavelength','run_fits.inputs.static_inputs.source_wavelength')
wf.connect_input('system','run_fits.inputs.static_inputs.system')
# inputs: lower and upper indices to run
wf.connect_input('lower_index',['t_filenames.inputs.lower_index',\
    't_q_I_files.inputs.lower_index','t_system_files.inputs.lower_index'])
wf.connect_input('upper_index',['t_filenames.inputs.upper_index',\
    't_q_I_files.inputs.upper_index','t_system_files.inputs.upper_index'])

wf.connect_workflow('read','batch_read.inputs.work_item')
wf.connect('header_files.outputs.file_list','batch_read.inputs.batch_inputs.header_file')

wf.connect('batch_read.outputs.batch_outputs',[\
    't_filenames.inputs.batch_outputs',\
    't_q_I_files.inputs.batch_outputs',
    't_system_files.inputs.batch_outputs'])
wf.set_op_inputs('t_system_files',x_key='time',y_key='system_file',x_sort_flag=False,x_shift_flag=True)
wf.set_op_inputs('t_filenames',x_key='time',y_key='filename',x_sort_flag=False,x_shift_flag=True)
wf.set_op_inputs('t_q_I_files',x_key='time',y_key='q_I_file',x_sort_flag=False,x_shift_flag=True)

wf.connect_workflow('read_and_fit','run_fits.inputs.work_item')
wf.connect('t_q_I_files.outputs.y','run_fits.inputs.batch_inputs.q_I_file')
wf.connect('t_system_files.outputs.y','run_fits.inputs.batch_inputs.system_file')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','batch_fit.wfm'))

