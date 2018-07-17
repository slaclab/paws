import os

from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()
wfmgr.load_packaged_wfm('DAQ.BL15.run_flow_integrate_bgsub_fit_pif')
wfmgr.workflows['run_reactor'].disable_op('stop_reactor')
wfmgr.load_packaged_wfm('IO.BL15.batch_read')
wfmgr.workflows['read'].disable_op('read_image')
wfmgr.add_workflow('run_batch')

wfmgr.load_operations('run_batch',
    run_bg_read='EXECUTION.Run',
    bg_files_vs_T='PACKAGING.BATCH.XYDataFromBatch',
    batch='EXECUTION.Batch',
    stop_reactor='DAQ.PLUGINS.StopFlowReactor')

wf = wfmgr.workflows['run_batch']
wf.connect_workflow('batch_read','run_bg_read.inputs.work_item')
wf.connect_input('bg_header_dir','run_bg_read.inputs.inputs.header_dir')
wf.connect_input('bg_header_regex','run_bg_read.inputs.inputs.header_regex')

wf.connect('run_bg_read.outputs.outputs.batch_outputs','bg_files_vs_T.inputs.batch_outputs')
wf.set_op_input('bg_files_vs_T','x_key','temperature')
wf.set_op_input('bg_files_vs_T','y_key','data_filepath')
wf.set_op_input('bg_files_vs_T','x_sort_flag',True)

wf.connect_workflow('main','batch.inputs.work_item')

wf.connect_input('recipes','batch.inputs.batch_inputs.recipe')
wf.connect_input('delay_times','batch.inputs.batch_inputs.delay_time')
wf.connect_input('filename_roots','batch.inputs.batch_inputs.filename_root')
wf.connect('bg_files_vs_T.outputs.x_y','batch.inputs.static_inputs.bg_files_vs_T')
#wf.connect_input('static_delay','batch.inputs.static_inputs.delay')
wf.connect_input('exposure_time','batch.inputs.static_inputs.exposure_time')
wf.connect_input('source_wavelength','batch.inputs.static_inputs.source_wavelength')
wf.connect_input('output_dir','batch.inputs.static_inputs.output_dir')
wf.connect_plugin('flow_reactor','stop_reactor.inputs.flow_reactor')
wf.set_dependency('stop_reactor','batch')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','batch_flow_integrate_bgsub_fit_pif.wfm'))


