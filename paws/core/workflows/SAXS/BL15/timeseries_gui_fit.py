import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools


# specify workflow names: 
wf_names = ['saxs_fit','read_header','main']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['header_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['header_batch'] = 'EXECUTION.Batch'
op_maps['main']['t_filenames'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['t_T'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['saxs_batch'] = 'EXECUTION.Batch'
op_maps['main']['t_params'] = 'PACKAGING.BATCH.XYDataFromBatch'

op_maps['read_header']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['read_header']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['read_header']['saxs_filepath'] = 'IO.FILESYSTEM.BuildFilePath'

op_maps['saxs_fit']['time'] = 'PACKAGING.Identity'
op_maps['saxs_fit']['read_saxs'] = 'IO.NUMPY.Loadtxt_q_I_dI'
op_maps['saxs_fit']['fit_saxs'] = 'PROCESSING.FITTING.XRSDFitGUI'
#op_maps['saxs_fit']['log_I'] = 'PROCESSING.BASIC.LogY'
#op_maps['saxs_fit']['log_Ifit'] = 'PROCESSING.BASIC.LogY'
#op_maps['saxs_fit']['output_CSV'] = 'IO.CSV.WriteArrayCSV'
#op_maps['saxs_fit']['params_path'] = 'IO.FILESYSTEM.BuildFilePath'
#op_maps['saxs_fit']['output_params'] = 'IO.YAML.SaveYAML'

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

wf.connect_output('t_filenames','t_filenames.outputs.x_y')
wf.connect_output('t_params','t_params.outputs.x_y')
wf.connect_output('t_T','t_T.outputs.x_y')

wf.set_op_input('header_batch','work_item','read_header','entire workflow')
wf.set_op_input('header_batch','input_arrays',['header_files.outputs.file_list'],'workflow item')
wf.set_op_input('header_batch','input_keys',['header_filepath'])

wf.set_op_input('t_filenames','batch_outputs','header_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('t_filenames','x_key','time')
wf.set_op_input('t_filenames','y_key','saxs_filepath')
wf.set_op_input('t_filenames','x_sort_flag',True)
wf.set_op_input('t_filenames','x_shift_flag',True)

wf.set_op_input('t_T','batch_outputs','header_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('t_T','x_key','time')
wf.set_op_input('t_T','y_key','temperature')
wf.set_op_input('t_T','x_sort_flag',True)
wf.set_op_input('t_T','x_shift_flag',True)

wf.set_op_input('saxs_batch','work_item','saxs_fit','entire workflow')
wf.set_op_input('saxs_batch','input_arrays',['t_filenames.outputs.x','t_filenames.outputs.y'],'workflow item')
wf.set_op_input('saxs_batch','input_keys',['time','saxs_filepath'])
wf.set_op_input('saxs_batch','pass_thru_params',{'populations':'fit_populations'})

wf.set_op_input('t_params','batch_outputs','saxs_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('t_params','x_key','time')
wf.set_op_input('t_params','y_key','fit_populations')
wf.set_op_input('t_params','x_sort_flag',True)
wf.set_op_input('t_params','x_shift_flag',True)



wf = wfmgr.workflows['read_header']

# input 0: header file
wf.connect_input('header_filepath','read_header.inputs.file_path') 

# inputs 1-2: keys for fetching time and temperature from header dictionary 
wf.connect_input('time_key','time_temp.inputs.temp_key')
wf.connect_input('temp_key','time_temp.inputs.temp_key')

# input 3: directory containing SAXS pattern csv files 
wf.connect_input('saxs_dir','saxs_filepath.inputs.dir_path')

wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('saxs_filepath','saxs_filepath.outputs.file_path')
wf.connect_output('saxs_filename','saxs_filepath.outputs.filename')

wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('time_temp','temp_key','TEMP')

wf.set_op_input('saxs_filepath','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('saxs_filepath','suffix','_dz_bgsub')
wf.set_op_input('saxs_filepath','ext','csv')



wf = wfmgr.workflows['saxs_fit']

wf.connect_input('time','time.inputs.data')
wf.connect_input('saxs_filepath','read_saxs.inputs.file_path')
wf.connect_input('populations','fit_saxs.inputs.populations')
wf.connect_input('fixed_params','fit_saxs.inputs.fixed_params')
wf.connect_input('bounds','fit_saxs.inputs.param_bounds')
wf.connect_input('constraints','fit_saxs.inputs.param_constraints')
wf.connect_input('source_wavelength','fit_saxs.inputs.source_wavelength')

wf.connect_output('q_I','read_saxs.outputs.q_I')
wf.connect_output('q_I_opt','fit_saxs.outputs.q_I_opt')
wf.connect_output('time','time.outputs.data')
wf.connect_output('fit_populations','fit_saxs.outputs.populations')

wf.set_op_input('read_saxs','delimiter',',')
wf.set_op_input('fit_saxs','q_I','read_saxs.outputs.q_I','workflow item')

#wf.set_op_input('log_I','x_y','read_spectrum.outputs.q_I','workflow item')
#wf.set_op_input('parameterize_spectrum','q_I','read_spectrum.outputs.q_I','workflow item')
#wf.set_op_input('fit_spectrum','populations','parameterize_spectrum.inputs.populations','workflow item')
#wf.set_op_input('log_Ifit','x_y','fit_spectrum.outputs.q_I_opt','workflow item')
#wf.set_op_input('output_CSV','array','fit_spectrum.outputs.q_I_opt','workflow item')
#wf.set_op_input('output_CSV','headers',['q (1/angstrom)','intensity (arb)'])
#wf.set_op_input('output_CSV','dir_path','read_spectrum.outputs.dir_path','workflow item')
#wf.set_op_input('output_CSV','filename','read_spectrum.outputs.filename','workflow item')
#wf.set_op_input('output_CSV','filetag','_fit')
#wf.set_op_input('params_path','dir_path','read_header.outputs.dir_path','workflow item')
#wf.set_op_input('params_path','filename','read_header.outputs.filename','workflow item')
#wf.set_op_input('params_path','suffix','_saxs_params')
#wf.set_op_input('params_path','ext','yaml')
#wf.set_op_input('output_params','file_path','params_path.outputs.file_path','workflow item')
#wf.set_op_input('output_params','data','fit_spectrum.outputs.params','workflow item')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','BL15','timeseries_gui_fit.wfl'),wfmgr)

