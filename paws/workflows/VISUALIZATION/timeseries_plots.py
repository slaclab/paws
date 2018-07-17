import os
from collections import OrderedDict

import paws
from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()
wfmgr.add_workflow('main')
wfmgr.load_packaged_wfm('IO.BL15.batch_read')
#wfmgr.add_workflow('read_header')
#wfmgr.add_workflow('plot')

wfmgr.add_operation('main','header_files','IO.FILESYSTEM.BuildFileList')
wfmgr.add_operation('main','header_batch','EXECUTION.Batch')
wfmgr.add_operation('main','t_filepaths','PACKAGING.BATCH.XYDataFromBatch')
wfmgr.add_operation('main','data_dir','PACKAGING.Container')
wfmgr.add_operation('main','batch_plot','EXECUTION.Batch')

wfmgr.add_operation('read_header','read_header','IO.BL15.ReadHeader_SSRL15')
wfmgr.add_operation('read_header','time_temp','PACKAGING.BL15.TimeTempFromHeader')
wfmgr.add_operation('read_header','data_filepath','IO.FILESYSTEM.BuildFilePath')

wfmgr.add_operation('plot','read_data','IO.NUMPY.Loadtxt_q_I_dI')
wfmgr.add_operation('plot','make_plot','PLOTTING.MakePlot')


wf = wfmgr.workflows['main']
wf.connect_input('header_dir','header_files.inputs.dir_path') 
wf.connect_input('header_regex','header_files.inputs.regex') 
wf.connect_input('data_dir','data_dir.inputs.data') 

wf.set_op_input('header_batch','work_item','read_header','entire workflow')
wf.set_op_input('header_batch','input_arrays',['header_files.outputs.file_list'],'workflow item')
wf.set_op_input('header_batch','input_keys',['header_filepath'])
wf.set_op_input('header_batch','static_inputs',['data_dir.inputs.data'],'workflow item')
wf.set_op_input('header_batch','static_input_keys',['data_dir'])

wf.set_op_input('t_filepaths','batch_outputs','header_batch.outputs.batch_outputs','workflow item')
wf.set_op_input('t_filepaths','x_key','time')
wf.set_op_input('t_filepaths','y_key','data_filepath')
wf.set_op_input('t_filepaths','x_sort_flag',True)
wf.set_op_input('t_filepaths','x_shift_flag',True)

wf.set_op_input('batch_plot','work_item','plot','entire workflow')
wf.set_op_input('batch_plot','input_arrays',['t_filepaths.outputs.y'],'workflow item')
wf.set_op_input('batch_plot','input_keys',['data_filepath'])


wf = wfmgr.workflows['read_header']
wf.connect_input('header_filepath','read_header.inputs.file_path') 
wf.connect_input('time_key','time_temp.inputs.time_key')
wf.connect_input('data_dir','data_filepath.inputs.dir_path')

wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('filename','read_header.outputs.filename')
wf.connect_output('data_filepath','data_filepath.outputs.file_path')

wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')

wf.set_op_input('data_filepath','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('data_filepath','suffix','_dz_bgsub')
wf.set_op_input('data_filepath','ext','csv')


wf = wfmgr.workflows['plot']
wf.connect_input('data_filepath','read_data.inputs.file_path')
wf.connect_input('logx','make_plot.inputs.logx')
wf.connect_input('logy','make_plot.inputs.logy')

wf.set_op_input('read_data','delimiter',',')
wf.set_op_input('make_plot','x_y_data','read_data.outputs.q_I','workflow item')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'workflows','VISUALIZATION','BL15','timeseries_plots.wfl'),wfmgr)

