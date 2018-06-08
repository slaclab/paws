import os
from collections import OrderedDict

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

# specify workflow names: 
wf_names = ['main','read_header','read_and_fit']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['header_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['header_batch'] = 'EXECUTION.Batch'
op_maps['main']['t_filepaths'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['t_filenames'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['saxs_dir'] = 'PACKAGING.Container'
op_maps['main']['saxs_batch'] = 'EXECUTION.Batch'

op_maps['read_header']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['read_header']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['read_header']['saxs_filepath'] = 'IO.FILESYSTEM.BuildFilePath'

op_maps['read_and_fit']['read_saxs'] = 'IO.NUMPY.Loadtxt_q_I_dI'
op_maps['read_and_fit']['populations_file'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['read_and_fit']['check_pops_file'] = 'IO.FILESYSTEM.CheckFilePath'
op_maps['read_and_fit']['conditional_read'] = 'EXECUTION.Conditional'
op_maps['read_and_fit']['read_pops'] = 'IO.YAML.LoadXRSDFit'
op_maps['read_and_fit']['populations'] = 'PACKAGING.Container'
op_maps['read_and_fit']['fixed_params'] = 'PACKAGING.Container'
op_maps['read_and_fit']['param_bounds'] = 'PACKAGING.Container'
op_maps['read_and_fit']['param_constraints'] = 'PACKAGING.Container'
op_maps['read_and_fit']['q_range'] = 'PACKAGING.Container'
op_maps['read_and_fit']['good_fit_prior'] = 'PACKAGING.Container'

op_maps['read_and_fit']['fit_saxs'] = 'PROCESSING.FITTING.XRSDFitGUI'
op_maps['read_and_fit']['conditional_save'] = 'EXECUTION.Conditional'
op_maps['read_and_fit']['save_populations'] = 'IO.YAML.SaveXRSDFit'

wfmgr = WfManager()
# add the workflows and activate/add the operations:
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)

wf = wfmgr.workflows['main']

# input 0: header files location
wf.connect_input('header_dir','header_files.inputs.dir_path') 
# input 1: header file regex
wf.connect_input('header_regex','header_files.inputs.regex') 
# input 2: saxs files location 
wf.connect_input('saxs_dir','saxs_dir.inputs.data') 
# inputs 3-4: lower and upper indices to run
wf.connect_input('lower_index',['t_filenames.inputs.lower_index','t_filepaths.inputs.lower_index'])
wf.connect_input('upper_index',['t_filenames.inputs.upper_index','t_filepaths.inputs.upper_index'])

wf.set_op_input('header_batch','work_item','read_header','entire workflow')
wf.set_op_input('header_batch','input_arrays',['header_files.outputs.file_list'],'workflow item')
wf.set_op_input('header_batch','input_keys',['header_filepath'])
wf.set_op_input('header_batch','static_inputs',['saxs_dir.inputs.data'],'workflow item')
wf.set_op_input('header_batch','static_input_keys',['saxs_dir'])

wf.set_op_input('t_filenames','batch_outputs','header_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('t_filenames','x_key','time')
wf.set_op_input('t_filenames','y_key','filename')
wf.set_op_input('t_filenames','x_sort_flag',True)
wf.set_op_input('t_filenames','x_shift_flag',True)

wf.set_op_input('t_filepaths','batch_outputs','header_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('t_filepaths','x_key','time')
wf.set_op_input('t_filepaths','y_key','saxs_filepath')
wf.set_op_input('t_filepaths','x_sort_flag',True)
wf.set_op_input('t_filepaths','x_shift_flag',True)

wf.set_op_input('saxs_batch','work_item','read_and_fit','entire workflow')
wf.set_op_input('saxs_batch','input_arrays',
    ['t_filenames.outputs.y','t_filepaths.outputs.y'],'workflow item')
wf.set_op_input('saxs_batch','input_keys',['filename','saxs_filepath'])
wf.set_op_input('saxs_batch','static_inputs',['saxs_dir.inputs.data'],'workflow item')
wf.set_op_input('saxs_batch','static_input_keys',['populations_dir'])
wf.set_op_input('saxs_batch','serial_params',
    {'populations':'populations','param_bounds':'param_bounds',
    'fixed_params':'fixed_params','param_constraints':'param_constraints',
    'q_range':'q_range','good_fit_prior':'good_fit_flag'})


wf = wfmgr.workflows['read_header']

# input 0: header file
wf.connect_input('header_filepath','read_header.inputs.file_path') 
# input 1: key for fetching time from header dictionary 
wf.connect_input('time_key','time_temp.inputs.time_key')
# input 3: directory containing SAXS pattern csv files 
wf.connect_input('saxs_dir','saxs_filepath.inputs.dir_path')

wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('filename','read_header.outputs.filename')
wf.connect_output('saxs_filepath','saxs_filepath.outputs.file_path')

wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')

wf.set_op_input('saxs_filepath','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('saxs_filepath','suffix','_dz_bgsub')
wf.set_op_input('saxs_filepath','ext','csv')


wf = wfmgr.workflows['read_and_fit']

wf.connect_input('filename','populations_file.inputs.filename')
wf.connect_input('saxs_filepath','read_saxs.inputs.file_path')
wf.connect_input('populations_dir','populations_file.inputs.dir_path')
wf.connect_input('populations','populations.inputs.data')
wf.connect_input('fixed_params','fixed_params.inputs.data')
wf.connect_input('param_bounds','param_bounds.inputs.data')
wf.connect_input('param_constraints','param_constraints.inputs.data')
wf.connect_input('q_range','q_range.inputs.data')
wf.connect_input('good_fit_prior','good_fit_prior.inputs.data')
wf.connect_input('source_wavelength','fit_saxs.inputs.source_wavelength')
wf.connect_output('populations','fit_saxs.outputs.populations')
wf.connect_output('fixed_params','fit_saxs.outputs.fixed_params')
wf.connect_output('param_bounds','fit_saxs.outputs.param_bounds')
wf.connect_output('param_constraints','fit_saxs.outputs.param_constraints')
wf.connect_output('q_range','fit_saxs.outputs.q_range')
wf.connect_output('good_fit_flag','fit_saxs.outputs.good_fit_flag')

wf.set_op_input('read_saxs','delimiter',',')
wf.set_op_input('populations_file','ext','yml')
wf.set_op_input('check_pops_file','file_path','populations_file.outputs.file_path','workflow item')

wf.set_op_input('conditional_read','condition','check_pops_file.outputs.file_exists','workflow item')
wf.set_op_input('conditional_read','run_condition',True)
wf.set_op_input('conditional_read','work_item','read_pops','workflow item')
wf.set_op_input('conditional_read','inputs',['populations_file.outputs.file_path'],'workflow item')
wf.set_op_input('conditional_read','input_keys',['file_path'])
wf.deactivate_op('read_pops')

wf.set_op_input('good_fit_prior','data',False)
wf.set_op_input('q_range','data',[0.,float('inf')])
wf.set_op_input('fit_saxs','q_I','read_saxs.outputs.q_I','workflow item')
wf.set_op_input('fit_saxs','q_range','q_range.inputs.data','workflow item')
wf.set_op_input('fit_saxs','good_fit_prior','good_fit_prior.inputs.data','workflow item')
wf.set_conditional_input('fit_saxs.inputs.populations',
    condition_uri='check_pops_file.outputs.file_exists',
    if_true_uri='conditional_read.outputs.outputs.populations',
    else_uri='populations.inputs.data')
wf.set_conditional_input('fit_saxs.inputs.fixed_params',
    condition_uri='check_pops_file.outputs.file_exists',
    if_true_uri='conditional_read.outputs.outputs.fixed_params',
    else_uri='fixed_params.inputs.data')
wf.set_conditional_input('fit_saxs.inputs.param_bounds',
    condition_uri='check_pops_file.outputs.file_exists',
    if_true_uri='conditional_read.outputs.outputs.param_bounds',
    else_uri='param_bounds.inputs.data')
wf.set_conditional_input('fit_saxs.inputs.param_constraints',
    condition_uri='check_pops_file.outputs.file_exists',
    if_true_uri='conditional_read.outputs.outputs.param_constraints',
    else_uri='param_constraints.inputs.data')


wf.set_op_input('conditional_save','work_item','save_populations','workflow item')
wf.set_op_input('conditional_save','inputs',
    ['populations_file.outputs.file_path',
    'fit_saxs.outputs.populations',
    'fit_saxs.outputs.fixed_params',
    'fit_saxs.outputs.param_bounds',
    'fit_saxs.outputs.param_constraints',
    'fit_saxs.outputs.report'],'workflow item')
wf.set_op_input('conditional_save','input_keys',
    ['file_path',
    'populations',
    'fixed_params',
    'param_bounds',
    'param_constraints',
    'report'])
wf.set_op_input('conditional_save','condition','fit_saxs.outputs.good_fit_flag','workflow item')
wf.set_op_input('conditional_save','run_condition',True)
wf.deactivate_op('save_populations')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'workflows','FITTING','BL15','timeseries_gui_fit.wfl'),wfmgr)

