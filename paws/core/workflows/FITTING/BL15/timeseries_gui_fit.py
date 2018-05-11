import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# specify workflow names: 
wf_names = ['main','read_header','saxs_fit']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['experiment_id'] = 'PACKAGING.Container'
op_maps['main']['header_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['header_batch'] = 'EXECUTION.Batch'
op_maps['main']['t_filenames'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['t_T'] = 'PACKAGING.BATCH.XYDataFromBatch'
op_maps['main']['saxs_batch'] = 'EXECUTION.Batch'
op_maps['main']['collect_pifs'] = 'PACKAGING.BATCH.ListFromBatch'
op_maps['main']['ship_pifs'] = 'IO.PIF.ShipToDataSet'

op_maps['read_header']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['read_header']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['read_header']['saxs_filepath'] = 'IO.FILESYSTEM.BuildFilePath'

op_maps['saxs_fit']['experiment_id'] = 'PACKAGING.Container'
op_maps['saxs_fit']['read_saxs'] = 'IO.NUMPY.Loadtxt_q_I_dI'
# TODO: operation to check filesystem for existing solution
# TODO: conditionally use existing solution to set up initial condition for fit 
op_maps['saxs_fit']['fit_saxs'] = 'PROCESSING.FITTING.XRSDFitGUI'
op_maps['saxs_fit']['make_pif'] = 'PACKAGING.PIF.PackXRSDPIF'

wfmgr = WfManager()
# add the workflows and activate/add the operations:
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)

pgmgr = wfmgr.plugin_manager
pgmgr.add_plugin('citrination_client','CitrinationClient')

wf = wfmgr.workflows['main']

# input 0: experiment ID 
wf.connect_input('experiment_id','experiment_id.inputs.data') 

# input 1: header files location
wf.connect_input('header_dir',['header_files.inputs.dir_path','ship_pifs.inputs.json_dirpath']) 

# input 2: header file regex
wf.connect_input('header_regex','header_files.inputs.regex') 

# input 3: Citrination dataset id (only needed if PIF records are being shipped) 
wf.connect_input('dataset_id','ship_pifs.inputs.dsid') 

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
wf.set_op_input('saxs_batch','input_arrays',['t_T.outputs.x','t_T.outputs.y','t_filenames.outputs.y'],'workflow item')
wf.set_op_input('saxs_batch','input_keys',['time','temperature','saxs_filepath'])
wf.set_op_input('saxs_batch','static_inputs',['experiment_id.inputs.data'],'workflow item')
wf.set_op_input('saxs_batch','static_input_keys',['experiment_id'])
wf.set_op_input('saxs_batch','serial_params',
    {'populations':'populations','param_bounds':'param_bounds','fixed_params':'fixed_params'})

wf.set_op_input('collect_pifs','batch_outputs','saxs_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('collect_pifs','output_key','pif')

wf.set_op_input('ship_pifs','pif','collect_pifs.outputs.data_list','workflow item')
wf.set_op_input('ship_pifs','client_plugin','citrination_client','plugin item')
wf.set_op_input('ship_pifs','dsid',None)            # dataset_id connects here
wf.set_op_input('ship_pifs','json_dirpath',None)    # header_dir connects here
wf.set_op_input('ship_pifs','json_filename','experiment_id.inputs.data','workflow item')
wf.set_op_input('ship_pifs','keep_json',True)
wf.set_op_input('ship_pifs','ship_flag',True)
wf.disable_op('collect_pifs')
wf.disable_op('ship_pifs')

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

wf.connect_input('experiment_id','experiment_id.inputs.data')
wf.connect_input('source_wavelength','fit_saxs.inputs.source_wavelength')
wf.connect_input('saxs_filepath','read_saxs.inputs.file_path')
wf.connect_input('time','make_pif.inputs.t_utc')
wf.connect_input('temperature','make_pif.inputs.temperature')
wf.connect_input('populations','fit_saxs.inputs.populations')
wf.connect_input('fixed_params','fit_saxs.inputs.fixed_params')
wf.connect_input('param_bounds','fit_saxs.inputs.param_bounds')
wf.connect_input('param_constraints','fit_saxs.inputs.param_constraints')

wf.connect_output('q_I','read_saxs.outputs.q_I')
wf.connect_output('q_I_opt','fit_saxs.outputs.q_I_opt')
wf.connect_output('populations','fit_saxs.outputs.populations')
wf.connect_output('fixed_params','fit_saxs.outputs.fixed_params')
wf.connect_output('param_bounds','fit_saxs.outputs.param_bounds')
wf.connect_output('param_constraints','fit_saxs.outputs.param_constraints')
wf.connect_output('pif','make_pif.outputs.pif')

wf.set_op_input('read_saxs','delimiter',',')
wf.set_op_input('fit_saxs','q_I','read_saxs.outputs.q_I','workflow item')

wf.set_op_input('make_pif','experiment_id','experiment_id.inputs.data','workflow item')
wf.set_op_input('make_pif','t_utc',None)            # time connects here
wf.set_op_input('make_pif','temperature',None)      # temperature connects here
wf.set_op_input('make_pif','q_I','read_saxs.outputs.q_I','workflow item')
wf.set_op_input('make_pif','populations','fit_saxs.outputs.populations','workflow item')
wf.disable_op('make_pif')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','FITTING','BL15','timeseries_gui_fit.wfl'),wfmgr)

