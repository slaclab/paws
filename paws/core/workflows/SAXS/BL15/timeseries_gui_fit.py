import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools


# specify workflow names: 
wf_names = ['saxs_fit','main']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['header_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['batch'] = 'EXECUTION.Batch'
op_maps['main']['fit_params'] = 'PACKAGING.BATCH.XYDataFromBatch'

op_maps['saxs_fit']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['saxs_fit']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['saxs_fit']['spectrum_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['saxs_fit']['read_spectrum'] = 'IO.NUMPY.Loadtxt_q_I_dI'
op_maps['saxs_fit']['populations_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['saxs_fit']['params_path'] = 'IO.FILESYSTEM.BuildFilePath'

op_maps['saxs_fit']['check_populations_file'] = 'IO.FILESYSTEM.CheckFilePath'
op_maps['saxs_fit']['check_params_file'] = 'IO.FILESYSTEM.CheckFilePath'
op_maps['saxs_fit']['fit_decision'] = 'EXECUTION.Conditional'

op_maps['saxs_fit']['fit_spectrum'] = 'PROCESSING.SAXS.SpectrumFitGUI'
op_maps['saxs_fit']['output_CSV'] = 'IO.CSV.WriteArrayCSV'
op_maps['saxs_fit']['output_populations'] = 'IO.YAML.SaveYAML'
op_maps['saxs_fit']['output_params'] = 'IO.YAML.SaveYAML'

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

wf.connect_output('batch_outputs','batch.outputs.batch_outputs')
wf.connect_output('params_vs_t','fit_params.outputs.x_y')

wf.set_op_input('batch','work_item','saxs_fit','entire workflow')
wf.set_op_input('batch','input_arrays',['header_files.outputs.file_list'],'workflow item')
wf.set_op_input('batch','input_keys',['header_file'])
wf.set_op_input('batch','pass_thru_params',{'params':'params','populations':'populations'})

wf.set_op_input('fit_params','batch_outputs','batch.outputs.batch_outputs','workflow item')
wf.set_op_input('fit_params','x_key','time')
wf.set_op_input('fit_params','x_sort_flag',True)
wf.set_op_input('fit_params','x_shift_flag',True)
wf.set_op_input('fit_params','y_key','fit_params')

wf = wfmgr.workflows['saxs_fit']

wf.disable_op('output_CSV')

# input 0: header file
wf.set_op_input('read_header','file_path',None) 
wf.connect_input('header_file','read_header.inputs.file_path') 

# input 1: spectrum directory, in case different from header 
wf.set_op_input('spectrum_path','dir_path',None)
wf.connect_input('spectrum_dir','spectrum_path.inputs.dir_path')

# input 2: key for fetching temperature from header dictionary 
wf.set_op_input('time_temp','temp_key','TEMP')
wf.connect_input('temp_key','time_temp.inputs.temp_key')

# input 3: populations and params dicts
wf.connect_input('populations','fit_spectrum.inputs.populations')
wf.connect_input('params','fit_spectrum.inputs.params')

wf.connect_output('filename','read_spectrum.outputs.filename')
wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('q_I','read_spectrum.outputs.q_I')
#wf.connect_output('q_logI','log_I.outputs.x_logy')
wf.connect_output('q_I_opt','fit_spectrum.outputs.q_I_opt')
#wf.connect_output('q_logI_opt','log_Ifit.outputs.x_logy')
wf.connect_output('populations','fit_spectrum.outputs.populations')
wf.connect_output('params','fit_spectrum.outputs.params')

wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('spectrum_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('spectrum_path','suffix','_dz_bgsub')
wf.set_op_input('spectrum_path','ext','csv')
wf.set_op_input('read_spectrum','file_path','spectrum_path.outputs.file_path','workflow item')
wf.set_op_input('read_spectrum','delimiter',',')

wf.set_op_input('params_path','dir_path','read_header.outputs.dir_path','workflow item')
wf.set_op_input('params_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('params_path','suffix','_saxs_params')
wf.set_op_input('params_path','ext','yaml')
wf.set_op_input('populations_path','dir_path','read_header.outputs.dir_path','workflow item')
wf.set_op_input('populations_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('populations_path','suffix','_populations')
wf.set_op_input('populations_path','ext','yaml')
wf.set_op_input('check_populations_file','file_path','populations_path.outputs.file_path','workflow item')
wf.set_op_input('check_params_file','file_path','populations_path.outputs.file_path','workflow item')
wf.set_op_input('fit_decision','work_item','fit_spectrum','workflow item')
wf.set_op_input('fit_decision','condition',
    ['check_populations_file.outputs.file_exists_flag',
    'check_params_file.outputs.file_exists_flag'],
    'workflow item')
wf.set_op_input('fit_decision','run_condition',[True,True])
wf.set_op_input('fit_decision','input_keys',['q_I'])
wf.set_op_input('fit_decision','inputs',['read_spectrum.outputs.q_I'],'workflow item')

#wf.set_op_input('log_I','x_y','read_spectrum.outputs.q_I','workflow item')
wf.set_op_input('fit_spectrum','q_I','read_spectrum.outputs.q_I','workflow item')
#wf.set_op_input('log_Ifit','x_y','fit_spectrum.outputs.q_I_opt','workflow item')
wf.set_op_input('output_CSV','array','fit_spectrum.outputs.q_I_opt','workflow item')
wf.set_op_input('output_CSV','headers',['q (1/angstrom)','intensity (arb)'])
wf.set_op_input('output_CSV','dir_path','read_spectrum.outputs.dir_path','workflow item')
wf.set_op_input('output_CSV','filename','read_spectrum.outputs.filename','workflow item')
wf.set_op_input('output_CSV','filetag','_fit')
wf.set_op_input('output_params','file_path','params_path.outputs.file_path','workflow item')
wf.set_op_input('output_params','data','fit_spectrum.outputs.params','workflow item')
wf.set_op_input('output_populations','file_path','populations_path.outputs.file_path','workflow item')
wf.set_op_input('output_populations','data','fit_spectrum.outputs.populations','workflow item')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','BL15','timeseries_gui_fit.wfl'),wfmgr)

