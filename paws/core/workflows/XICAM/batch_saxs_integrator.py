import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# specify workflow names: 
wf_names = ['saxs_integrator','batch_saxs_integrator']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['batch_saxs_integrator']['Integrator Setup'] = 'PROCESSING.INTEGRATION.BuildPyFAIIntegrator'
op_maps['batch_saxs_integrator']['Batch Execution'] = 'EXECUTION.Batch'
op_maps['saxs_integrator']['Read Image'] = 'IO.IMAGE.FabIOOpen'
op_maps['saxs_integrator']['Integrate to 2d'] = 'PROCESSING.INTEGRATION.ApplyIntegrator2d'
op_maps['saxs_integrator']['Integrate to 1d'] = 'PROCESSING.INTEGRATION.ApplyIntegrator1d'
op_maps['saxs_integrator']['log(I) 2d'] = 'PROCESSING.BASIC.ArrayLog'
op_maps['saxs_integrator']['log(I) 1d'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_integrator']['Output CSV'] = 'IO.CSV.WriteArrayCSV'
op_maps['saxs_integrator']['Output Image'] = 'IO.IMAGE.FabIOWrite'

wfmgr = WfManager()
# add the workflows and activate/add the operations:
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)


wf = wfmgr.workflows['saxs_integrator']

# input 0: the file path
wf.set_op_input('Read Image','file_path',None)
wf.connect_input('image_path','Read Image.inputs.file_path')

# input 1: the integrator 
wf.set_op_input('Integrate to 1d','integrator',None,'runtime')
wf.set_op_input('Integrate to 2d','integrator',None,'runtime')
wf.connect_input('integrator',
    ['Integrate to 1d.inputs.integrator',
    'Integrate to 2d.inputs.integrator'])

# If we wanted to save some of the outputs:
#wf.connect_output('q_I','Integrate to 1d.outputs.q_I')
#wf.connect_output('chi','Integrate to 2d.outputs.chi')
#wf.connect_output('I_at_q_chi','Integrate to 2d.outputs.I_at_q_chi')

# By default, disable the output operations
wf.disable_op('Output CSV')
wf.disable_op('Output Image')

# the image data is taken from the upstream "Read Image" outputs
wf.set_op_input('Integrate to 1d','image_data','Read Image.outputs.image_data','workflow item')
wf.set_op_input('Integrate to 2d','image_data','Read Image.outputs.image_data','workflow item')

# log(I) operations take data from the corresponding integration outputs
wf.set_op_input('log(I) 1d','x_y','Integrate to 1d.outputs.q_I','workflow item')
wf.set_op_input('log(I) 2d','x','Integrate to 2d.outputs.I_at_q_chi','workflow item')

# data-output operations take data and filepaths from upstream operation outputs
wf.set_op_input('Output CSV','array','Integrate to 1d.outputs.q_I','workflow item')
wf.set_op_input('Output CSV','headers',['q','I'])
wf.set_op_input('Output CSV','dir_path','Read Image.outputs.dir_path','workflow item')
wf.set_op_input('Output CSV','filename','Read Image.outputs.filename','workflow item')
wf.set_op_input('Output CSV','filetag','_q_I')
wf.set_op_input('Output Image','image_data','Integrate to 2d.outputs.I_at_q_chi','workflow item')
# TODO: a more thoughtful header for output images
wf.set_op_input('Output Image','header',{})
wf.set_op_input('Output Image','dir_path','Read Image.outputs.dir_path','workflow item')
wf.set_op_input('Output Image','filename','Read Image.outputs.filename','workflow item')
wf.set_op_input('Output Image','filetag','_integrated')
wf.set_op_input('Output Image','overwrite',True)
wf.set_op_input('Output Image','ext','.edf')



wf = wfmgr.workflows['batch_saxs_integrator']

# input 0: the calibration parameters
# This is read in from Xi-cam at runtime 
wf.set_op_input('Integrator Setup','poni_dict',None)
wf.connect_input('poni_dict','Integrator Setup.inputs.poni_dict')

# input 1: the list of images
# This is read in from Xi-cam at runtime
wf.set_op_input('Batch Execution','input_arrays',None)

wf.set_op_input('Batch Execution','work_item','saxs_integrator','entire workflow')
wf.set_op_input('Batch Execution','input_keys',['image_path'])
wf.set_op_input('Batch Execution','static_inputs',['Integrator Setup.outputs.integrator'],'workflow item')
wf.set_op_input('Batch Execution','static_input_keys',['integrator'])

# save the workflows in a .wfl file
pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','XICAM','batch_saxs_integrator.wfl'),wfmgr)

