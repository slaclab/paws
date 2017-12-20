import os

import paws.api
from paws.core import pawstools

paw = paws.api.start()

### (0) Activate all the ops that will be used
paw.activate_op('IO.CALIBRATION.ReadPONI')
paw.activate_op('PROCESSING.INTEGRATION.BuildPyFAIIntegrator')
paw.activate_op('IO.IMAGE.FabIOOpen')
paw.activate_op('PROCESSING.INTEGRATION.ApplyIntegrator1d')
paw.activate_op('PACKAGING.Window')
paw.activate_op('PROCESSING.ZINGERS.EasyZingers1d')
paw.activate_op('PROCESSING.BASIC.LogY')
paw.activate_op('IO.CSV.WriteArrayCSV')

### (1) Add workflows and name them
paw.add_wf('saxs_integrate')

### (2) Add ops to the workflows
paw.select_wf('saxs_integrate')
paw.add_op('read_poni','IO.CALIBRATION.ReadPONI')
paw.add_op('read_image','IO.IMAGE.FabIOOpen')
paw.add_op('build_integrator','PROCESSING.INTEGRATION.BuildPyFAIIntegrator')
paw.add_op('integrate','PROCESSING.INTEGRATION.ApplyIntegrator1d')
paw.add_op('window','PACKAGING.Window')
paw.add_op('dezinger','PROCESSING.ZINGERS.EasyZingers1d')
paw.add_op('logI','PROCESSING.BASIC.LogY')
paw.add_op('write_csv','IO.CSV.WriteArrayCSV')

### (3) add Workflow inputs and connect them to Operation inputs 
# input 1: path to .nika calibration file
paw.set_input('read_poni','file_path',None)
paw.add_wf_input('poni_file','read_poni.inputs.file_path')
# input 2: path to image file
paw.set_input('read_image','file_path',None)
paw.add_wf_input('file_path','read_image.inputs.file_path')
# inputs 3 and 4: q-range for data windowing
paw.set_input('window','x_min',None)
paw.set_input('window','x_max',None)
paw.add_wf_input('q_min','window.inputs.x_min')
paw.add_wf_input('q_max','window.inputs.x_max')
# input 5: path to output directory
#paw.add_wf_input('output_dir','write_csv.inputs.dir_path')

### (4) set up the rest of the Operation IO routing
paw.set_input('build_integrator','poni_dict','read_poni.outputs.poni_dict','workflow item')
paw.set_input('integrate','image_data','read_image.outputs.image_data','workflow item')
paw.set_input('integrate','integrator','build_integrator.outputs.integrator','workflow item')
paw.set_input('window','x_y','integrate.outputs.q_I','workflow item')
paw.set_input('dezinger','q_I','window.outputs.x_y_window','workflow item')
paw.set_input('logI','x_y','dezinger.outputs.q_I_dz','workflow item')
paw.set_input('write_csv','array','dezinger.outputs.q_I_dz','workflow item')
paw.set_input('write_csv','headers',['q (1/angstrom)','intensity (arb)'])
paw.set_input('write_csv','dir_path','read_image.outputs.dir_path','workflow item')
paw.set_input('write_csv','filename','read_image.outputs.filename','workflow item')
paw.set_input('write_csv','filetag','_dz')

