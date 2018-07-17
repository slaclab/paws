import os

from paws.workflows.WfManager import WfManager
from paws import pawstools

wfmgr = WfManager()
wfmgr.load_packaged_wfm('DAQ.BL15.run_flow_integrate')
wfmgr.add_workflow('run_batch')

wfmgr.load_operations('run_batch',
    batch='EXECUTION.Batch',
    stop_reactor='DAQ.PLUGINS.StopFlowReactor')

wfmgr.workflows['run_batch'].connect_workflow('main','batch.inputs.work_item')
wfmgr.workflows['run_reactor'].disable_op('stop_reactor')

wf = wfmgr.workflows['run_batch']
wf.connect_input('recipes','batch.inputs.batch_inputs.recipe')
wf.connect_input('filename_roots','batch.inputs.batch_inputs.filename_root')
wf.connect_input('delay','batch.inputs.static_inputs.delay')
wf.connect_input('exposure_time','batch.inputs.static_inputs.exposure_time')
wf.connect_input('source_wavelength','batch.inputs.static_inputs.source_wavelength')
wf.connect_input('output_dir','batch.inputs.static_inputs.output_dir')
wf.connect_plugin('flow_reactor','stop_reactor.inputs.flow_reactor')
wf.set_dependency('stop_reactor','batch')

wfmgr.save_to_wfm(os.path.join(pawstools.sourcedir,'workflows','DAQ','BL15','batch_flow_integrate.wfm'))

