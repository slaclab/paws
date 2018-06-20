import os

from paws import pawstools
from paws.workflows.WfManager import WfManager

wfmgr = WfManager()
wfmgr.add_workflow('main')
wfmgr.load_operations('main',
    header_files='IO.FILESYSTEM.BuildFileList',
    header_batch='EXECUTION.Batch',
    t_filepaths='PACKAGING.BATCH.XYDataFromBatch',
    t_filenames='PACKAGING.BATCH.XYDataFromBatch',
    batch_fit='EXECUTION.Batch'
    )

wfmgr.load_packaged_workflow('read_header','IO.BL15.read_header')
wfmgr.load_packaged_workflow('read_and_fit','FITTING.BL15.read_and_fit')

wf = wfmgr.workflows['main']

# input: header files location and regex
wf.connect_input('header_dir','header_files.inputs.dir_path') 
wf.connect_input('header_regex','header_files.inputs.regex') 
# inputs: directories for finding image and data files 
wf.connect_input('data_dir',[\
    'header_batch.inputs.static_inputs.data_dir',\
    'batch_fit.inputs.static_inputs.populations_dir']) 
#wf.connect_input('image_dir','header_batch.inputs.static_inputs.image_dir') 
# inputs: initial conditions, bounds, constraints, for fitting
wf.connect_input('populations','batch_fit.inputs.static_inputs.populations')
wf.connect_input('fixed_params','batch_fit.inputs.static_inputs.fixed_params')
wf.connect_input('param_bounds','batch_fit.inputs.static_inputs.param_bounds')
wf.connect_input('param_constraints','batch_fit.inputs.static_inputs.param_constraints')
# inputs: lower and upper indices to run
wf.connect_input('lower_index',['t_filenames.inputs.lower_index','t_filepaths.inputs.lower_index'])
wf.connect_input('upper_index',['t_filenames.inputs.upper_index','t_filepaths.inputs.upper_index'])

wf.connect_workflow('read_header','header_batch.inputs.work_item')
wf.connect('header_files.outputs.file_list','header_batch.inputs.batch_inputs.header_filepath')

wf.connect('header_batch.outputs.batch_outputs',[\
    't_filenames.inputs.batch_outputs',\
    't_filepaths.inputs.batch_outputs'])
wf.set_op_inputs('t_filenames',x_key='time',y_key='filename',x_sort_flag=False,x_shift_flag=True)
wf.set_op_inputs('t_filepaths',x_key='time',y_key='data_filepath',x_sort_flag=False,x_shift_flag=True)

wf.connect_workflow('read_and_fit','batch_fit.inputs.work_item')
wf.connect('t_filenames.outputs.y','batch_fit.inputs.batch_inputs.filename')
wf.connect('t_filepaths.outputs.y','batch_fit.inputs.batch_inputs.data_filepath')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','batch_fit.wfm'))

