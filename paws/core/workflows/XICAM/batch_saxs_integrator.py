import os
from collections import OrderedDict

import paws.api
from paws.core import pawstools

paw = paws.api.start()
# name the workflows:
wf_names = ['saxs_integrator','batch_saxs_integrator']
# name the operations:
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
# name ops for batch workflow:
op_maps['batch_saxs_integrator']['Integrator Setup'] = 'PROCESSING.INTEGRATION.BuildPyFAIIntegrator'
op_maps['batch_saxs_integrator']['Batch Execution'] = 'EXECUTION.Batch'
# name ops for processing workflow:
op_maps['saxs_integrator']['Read Image'] = 'IO.IMAGE.FabIOOpen'
op_maps['saxs_integrator']['Integrate to 2d'] = 'PROCESSING.INTEGRATION.ApplyIntegrator2d'
op_maps['saxs_integrator']['Integrate to 1d'] = 'PROCESSING.INTEGRATION.ApplyIntegrator1d'
op_maps['saxs_integrator']['log(I) 2d'] = 'PROCESSING.BASIC.ArrayLog'
op_maps['saxs_integrator']['log(I) 1d'] = 'PROCESSING.BASIC.LogY'
op_maps['saxs_integrator']['Output CSV'] = 'IO.CSV.WriteArrayCSV'
op_maps['saxs_integrator']['Output Image'] = 'IO.IMAGE.FabIOWrite'
# add the workflows and activate the operations:
for wf_name,op_map in op_maps.items():
    paw.add_wf(wf_name)
    for op_name,op_uri in op_map.items():
        paw.activate_op(op_uri)       


#### SAXS INTEGRATOR WORKFLOW SETUP ####
paw.select_wf('saxs_integrator')
for op_name,op_uri in op_maps['saxs_integrator'].items(): 
    paw.add_op(op_name,op_uri)

# the file paths will be iterated by the batch executor-
# just for clarity, set it to None (strictly not necessary) 
paw.set_input('Read Image','file_path',None)

# the image data is taken from the upstream "Read Image" outputs
paw.set_input('Integrate to 1d','image_data','Read Image.outputs.image_data','workflow item')
paw.set_input('Integrate to 2d','image_data','Read Image.outputs.image_data','workflow item')
# the integrator must be set to "runtime" type,
# indicating that this input should be skipped if/when the workflow is serialized,
# because PyFAI.AzimuthalIntegrator objects cannot be serialized
paw.set_input('Integrate to 1d','integrator',None,'runtime')
paw.set_input('Integrate to 2d','integrator',None,'runtime')

# log(I) operations take data from the corresponding integration outputs
paw.set_input('log(I) 1d','x_y','Integrate to 1d.outputs.q_I','workflow item')
paw.set_input('log(I) 2d','x','Integrate to 2d.outputs.I_at_q_chi','workflow item')

# data-output operations take data and filepaths from upstream operation outputs
paw.set_input('Output CSV','array','Integrate to 1d.outputs.q_I','workflow item')
paw.set_input('Output CSV','headers',['q','I'])
paw.set_input('Output CSV','dir_path','Read Image.outputs.dir_path','workflow item')
paw.set_input('Output CSV','filename','Read Image.outputs.filename','workflow item')
paw.set_input('Output CSV','filetag','_q_I')
paw.set_input('Output Image','image_data','Integrate to 2d.outputs.I_at_q_chi','workflow item')
# TODO: a more thoughtful header for output images
paw.set_input('Output Image','header',{})
paw.set_input('Output Image','dir_path','Read Image.outputs.dir_path','workflow item')
paw.set_input('Output Image','filename','Read Image.outputs.filename','workflow item')
paw.set_input('Output Image','filetag','_integrated')
paw.set_input('Output Image','overwrite',True)
paw.set_input('Output Image','ext','.edf')

# By default, deactivate the output operations
paw.disable_op('Output CSV')
paw.disable_op('Output Image')

# Add workflow inputs and outputs:
# inputs are the keys used by the batch executor,
# and outputs dictate which data items will be saved.
# By default, no outputs are saved, to keep memory footprint low.
paw.add_wf_input('image_path',
    'Read Image.inputs.file_path')
paw.add_wf_input('integrator',
    ['Integrate to 1d.inputs.integrator',
    'Integrate to 2d.inputs.integrator'])
# If we wanted to save some of the outputs,
# we could do this:
#paw.add_wf_output('q_I','Integrate to 1d.outputs.q_I')
#paw.add_wf_output('chi','Integrate to 2d.outputs.chi')
#paw.add_wf_output('I_at_q_chi','Integrate to 2d.outputs.I_at_q_chi')


#### BATCH EXECUTION WORKFLOW SETUP ####
paw.select_wf('batch_saxs_integrator')
for op_name,op_uri in op_maps['batch_saxs_integrator'].items(): 
    paw.add_op(op_name,op_uri)

# The Integrator setup dict will be read in,
# from Xi-cam's internal variables,
# when execution is triggered.
paw.set_input('Integrator Setup','poni_dict',None)
paw.set_input('Batch Execution','work_item','saxs_integrator','entire workflow')
paw.set_input('Batch Execution','input_keys',['image_path'])
# The list of images will be read in,
# from the Xi-cam gui,
# when execution is triggered.
paw.set_input('Batch Execution','input_arrays',None)
# The integrator itself will be fed to saxs_integrator
# as a static input, i.e.,
# the same integrator will be used across the entire batch.
paw.set_input('Batch Execution','static_input_keys',['integrator'])
paw.set_input('Batch Execution','static_inputs',['Integrator Setup.outputs.integrator'],'workflow item')

# save the workflows in a .wfl file
paw.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','XICAM','batch_saxs_integrator.wfl'))

