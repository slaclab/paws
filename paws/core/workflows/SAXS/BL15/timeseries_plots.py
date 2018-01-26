import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools


# specify workflow names: 
wf_names = ['read_files','main']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['header_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['batch'] = 'EXECUTION.Batch'
#op_maps['main']['get_t_r0'] = 'PACKAGING.BATCH.XYDataFromBatch'
#op_maps['main']['write_t_r0'] = 'IO.CSV.WriteArrayCSV'

op_maps['read_files']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['read_files']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['read_files']['populations_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['read_files']['read_populations'] = 'IO.YAML.LoadYAML'
op_maps['read_files']['params_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['read_files']['read_params'] = 'IO.YAML.LoadYAML'

#
#
#
#
op_maps['read_files']['write_params'] = 'IO.YAML.SaveYAML'
#
#
#
#

wfmgr = WfManager()
# add the workflows and activate/add the operations:
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)

wf = wfmgr.workflows['main']

# input 0: header files location
wf.set_op_input('header_files','dir_path',None) 
wf.connect_input('header_dir','header_files.inputs.dir_path') 

# input 1: header file regex
wf.set_op_input('header_files','regex','*.txt') 
wf.connect_input('header_regex','header_files.inputs.regex') 

wf.connect_output('r0_vs_t','get_t_r0.outputs.x_y')

wf.set_op_input('batch','work_item','read_files','entire workflow')
wf.set_op_input('batch','input_arrays',['header_files.outputs.file_list'],'workflow item')
wf.set_op_input('batch','input_keys',['header_file'])

#wf.set_op_input('get_t_r0','batch_outputs','batch.outputs.batch_outputs','workflow item')
#wf.set_op_input('get_t_r0','x_key','time')
#wf.set_op_input('get_t_r0','y_key','r0_sphere')
#wf.set_op_input('get_t_r0','x_shift_flag',True)
#wf.set_op_input('get_t_r0','x_sort_flag',True)

#wf.set_op_input('write_t_r0','array','get_t_r0.outputs.x_y','workflow item')
#wf.set_op_input('write_t_r0','headers',['time (s)','r0_sphere (A)'])
#wf.set_op_input('write_t_r0','dir_path','header_files.inputs.dir_path','workflow item')
#wf.set_op_input('write_t_r0','filename','t_r0_sphere')

wf = wfmgr.workflows['read_files']

# input 0: header file
wf.set_op_input('read_header','file_path',None) 
wf.connect_input('header_file','read_header.inputs.file_path') 

# input 1: key for fetching temperature from header dictionary 
wf.set_op_input('time_temp','temp_key','TEMP')
wf.connect_input('temp_key','time_temp.inputs.temp_key')

wf.connect_output('filename','read_spectrum.outputs.filename')
wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('populations','read_populations.outputs.yaml_output')
wf.connect_output('params','read_params.outputs.yaml_output')
wf.connect_output('r0_sphere','read_params.outputs.yaml_output.r0_sphere')

wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('populations_path','dir_path','read_header.outputs.dir_path','workflow item')
wf.set_op_input('populations_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('populations_path','suffix','_populations')
wf.set_op_input('populations_path','ext','yaml')
wf.set_op_input('read_populations','file_path','populations_path.outputs.file_path','workflow item')
wf.set_op_input('params_path','dir_path','read_header.outputs.dir_path','workflow item')
wf.set_op_input('params_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('params_path','suffix','_saxs_params')
wf.set_op_input('params_path','ext','yaml')
wf.set_op_input('read_params','file_path','params_path.outputs.file_path','workflow item')

#
#
#
#
wf.set_op_input('write_params','file_path','read_params.inputs.file_path','workflow item')
wf.set_op_input('write_params','data','read_params.outputs.yaml_output','workflow item')
#
#
#
#

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','BL15','timeseries_plots.wfl'),wfmgr)

