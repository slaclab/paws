import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# specify workflow names: 
wf_names = ['main','read_header','postprocess']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['header_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['header_batch'] = 'EXECUTION.Batch'
op_maps['main']['t_filepaths'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['t_filenames'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['saxs_dir'] = 'PACKAGING.Container'
op_maps['main']['batch_postprocess'] = 'EXECUTION.Batch'
op_maps['main']['t_T'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['t_populations'] = 'PACKAGING.BATCH.XYDataFromBatch'
#op_maps['main']['collect_pifs'] = 'PACKAGING.BATCH.ListFromBatch'
#op_maps['main']['ship_pifs'] = 'IO.PIF.ShipToDataSet'

op_maps['read_header']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['read_header']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['read_header']['saxs_filepath'] = 'IO.FILESYSTEM.BuildFilePath'

op_maps['postprocess']['read_saxs'] = 'IO.NUMPY.Loadtxt_q_I_dI'
op_maps['postprocess']['populations_file'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['postprocess']['check_pops_file'] = 'IO.FILESYSTEM.CheckFilePath'
op_maps['postprocess']['conditional_read'] = 'EXECUTION.Conditional'
op_maps['postprocess']['time'] = 'PACKAGING.Container'
op_maps['postprocess']['read_pops'] = 'IO.YAML.LoadXRSDFit'
#op_maps['postprocess']['make_pif'] = 'PACKAGING.PIF.PackXRSDPIF'

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

wf.connect_output('t_T','t_T.outputs.x_y')
wf.connect_output('t_filenames','t_filenames.outputs.x_y')
wf.connect_output('t_populations','t_populations.outputs.x_y')

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

wf.set_op_input('batch_postprocess','work_item','postprocess','entire workflow')
wf.set_op_input('batch_postprocess','input_arrays',
    ['t_filenames.outputs.y','t_filepaths.outputs.y','t_filenames.outputs.x'],'workflow item')
wf.set_op_input('batch_postprocess','input_keys',['filename','saxs_filepath','time'])
wf.set_op_input('batch_postprocess','static_inputs',['saxs_dir.inputs.data'],'workflow item')
wf.set_op_input('batch_postprocess','static_input_keys',['populations_dir'])

wf.set_op_input('t_T','batch_outputs','header_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('t_T','x_key','time')
wf.set_op_input('t_T','y_key','temperature')
wf.set_op_input('t_T','x_sort_flag',True)
wf.set_op_input('t_T','x_shift_flag',True)

wf.set_op_input('t_populations','batch_outputs','batch_postprocess.outputs.batch_outputs','workflow item')
wf.set_op_input('t_populations','x_key','time')
wf.set_op_input('t_populations','y_key','populations')
wf.set_op_input('t_populations','x_sort_flag',True)
wf.set_op_input('t_populations','x_shift_flag',True)

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
wf.set_op_input('time_temp','temp_key','TEMP')

wf.set_op_input('saxs_filepath','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('saxs_filepath','suffix','_dz_bgsub')
wf.set_op_input('saxs_filepath','ext','csv')


wf = wfmgr.workflows['postprocess']

wf.connect_input('time','time.inputs.data')
wf.connect_input('filename','populations_file.inputs.filename')
wf.connect_input('saxs_filepath','read_saxs.inputs.file_path')
wf.connect_input('populations_dir','populations_file.inputs.dir_path')
wf.connect_output('time','time.inputs.data')
wf.connect_output('populations','read_pops.outputs.populations')
#wf.connect_output('pif','make_pif.outputs.pif')

wf.set_op_input('read_saxs','delimiter',',')
wf.set_op_input('populations_file','ext','yml')
wf.set_op_input('check_pops_file','file_path','populations_file.outputs.file_path','workflow item')

wf.set_op_input('conditional_read','condition','check_pops_file.outputs.file_exists','workflow item')
wf.set_op_input('conditional_read','run_condition',True)
wf.set_op_input('conditional_read','work_item','read_pops','workflow item')
wf.set_op_input('conditional_read','inputs',['populations_file.outputs.file_path'],'workflow item')
wf.set_op_input('conditional_read','input_keys',['file_path'])
wf.deactivate_op('read_pops')

#wf.set_op_input('make_pif','experiment_id','','workflow item') 
#wf.set_op_input('make_pif','t_utc','','workflow item')
#wf.set_op_input('make_pif','temperature','','workflow item')
#wf.set_op_input('make_pif','q_I','','workflow item')
#wf.set_op_input('make_pif','populations','','workflow item')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','FITTING','BL15','timeseries_postprocess.wfl'),wfmgr)

